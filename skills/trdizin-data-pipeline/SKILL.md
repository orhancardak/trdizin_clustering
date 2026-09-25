---
name: trdizin-data-pipeline
description: TR Dizin API'sinden veri çekme, embedding_text oluşturma, MPNet embedding üretimi, embedding index eşleme veya Qdrant yükleme ile ilgili herhangi bir görevde kullan. data_pipeline/*.py dosyalarına dokunmadan önce bu skill'i oku.
---

# TR Dizin Veri Hattı Skill'i

## Ne zaman aktif olunacak
`data_pipeline/` klasöründeki herhangi bir script değiştirilecek, yeni bir alan/sütun eklenecek veya
embedding üretim akışı hakkında soru sorulduğunda.

## Pipeline sırası (bozulmaması gereken sıra)
1. `fetch_balanced_trdizin.py` → `data/balanced_articles.csv`, `data/article_subjects.csv`
2. `generate_mpnet_embeddings_20k.py` → `embeddings/mpnet_multilingual_embeddings.npy`
3. `build_embedding_index.py` → `embeddings/article_embedding_index.csv`
4. `load_all_articles_to_qdrant.py` → Qdrant `trdizin_articles` koleksiyonu

Bu sıra bozulursa (örn. embedding_text değiştiği halde embedding yeniden üretilmezse) index ile embedding
matrisi arasında sessiz bir tutarsızlık oluşur — bu en tehlikeli hata sınıfıdır, mutlaka uyar.

## Kesin kurallar

### 1. `embedding_text` inşası
```
embedding_text = Başlık + ". " + Özet + ". Keywords: " + Anahtar_Kelimeler
```
- Dil önceliği: Türkçe (`TUR`) varsa o seçilir; yoksa İngilizce (`ENG`); o da yoksa ilk kullanılabilir kayıt.
- Bu mantık `build_article_record()` ve `choose_article_text()` fonksiyonlarında yaşıyor.
- Başlıksız kayıtlar, başlık+özet ikisi de boş olanlar veya `embedding_text` boş çıkanlar elenir.
- `external_id` üzerinden dedup yapılır — her makaleden tek kayıt.

### 2. Operasyonel vs. metodolojik ayrım
`TARGET_PER_SUBJECT=750`, `PAGE_SIZE=50`, `REQUEST_SLEEP=0.25` → bunlar **operasyonel/heuristic**
ayarlardır (API kotası, sunucu yükü, dengeli başlangıç kümesi için). Metodolojik parametre değildirler,
gerekirse serbestçe ayarlanabilir — ama değiştirirken kullanıcıya API'nin rate-limit davranışını
hatırlat.

### 3. Embedding modeli
- Model: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- Boyut: 768, `normalize_embeddings=True`, metrik: Cosine (L2 normalize edilmiş vektörlerin iç çarpımı)
- Model değişikliği istenirse önce `evaluation/compare_embedding_models.py` ile karşılaştırma çalıştırılmalı
  (bkz. `results/embedding_model_comparison.csv`) — mevcut kıyasta MPNet, E5 ve BGE-M3'ü Silhouette,
  Davies-Bouldin, Calinski-Harabasz ve singleton küme sayısında geçiyor.

### 4. Index tutarlılığı
`build_embedding_index.py`, `.npy` satır sırası ile `external_id` arasında eşleme kurar. Her satır
ekleme/silme işleminden sonra `len(embeddings) == len(index_csv) == len(balanced_articles dedup)`
eşitliğini kontrol et.

### 5. Qdrant
- Collection: `trdizin_articles`
- Named vector: `mpnet_v1` (768D, Cosine)
- Yükleme sırasında `external_id`'yi Qdrant point id'si olarak kullan (kNN sorgularında self-neighbor
  filtrelemesi buna dayanıyor, bkz. `hdbscan-anomaly-pipeline` skill).

## Çıktı formatı
Bir pipeline scripti değiştirdiğinde şunu raporla:
- Hangi dosya(lar) değişti
- Hangi downstream adımın (embedding / index / Qdrant / clustering) yeniden çalıştırılması gerekiyor
- Küçük bir örneklemde (tüm 20.902 makale değil) test edilip edilmediği
