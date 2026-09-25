---
name: hdbscan-anomaly-pipeline
description: clustering/hdbscan/ altındaki UMAP 15D → HDBSCAN → GLOSH → Qdrant exact kNN → şüpheli_mi → final filtreler → risk_skoru üretim hattıyla ilgili her görevde, ya da dashboard/kod/dokümanda anomali skorlarının nasıl yorumlanacağı sorulduğunda kullan. Bu proje için en kritik skill — metodolojik hataların çoğu buradan sızar.
---

# HDBSCAN Anomali Tespit Hattı Skill'i

## Ne zaman aktif olunacak
- `clustering/hdbscan/outlier_detector.py`, `run_hdbscan_pipeline.py`, `cluster_labeler.py`,
  `generate_hdbscan_umap_20k.py`, `ablation_study.py`, `post_ablation_analysis.py` değiştirilirken
- GLOSH, risk_skoru, knn_impurity, label_sim_fark gibi bir alan dashboard'da veya raporda sunulurken
- Kullanıcı "bu eşiği değiştir / bu skoru şöyle yorumla" dediğinde

Tüm sayısal sabitlerin tam listesi için `params.md` dosyasına bak.

## Pipeline (sıra değişmez)
```
768D MPNet Embedding
   → 15D UMAP (ara temsil, SADECE kümeleme için)
   → HDBSCAN (yoğunluk kümeleme)
   → GLOSH (outlier_scores_, yoğunluk aykırılık skoru)
   → Qdrant exact kNN (k=10, gerçek komşuluk doğrulaması)
   → şüpheli_mi (ön aday kararı)
   → final filtreler (ana disiplin / alt alan maskeleri)
   → risk_skoru (manuel inceleme önceliği)
```
Ayrıca **paralel ve bağımsız** olarak: `generate_hdbscan_umap_20k.py` içinde 2D UMAP üretilir —
bu SADECE `embeddings/umap_2d_coordinates.csv`'ye yazılır ve dashboard görselleştirmesinde kullanılır.

## En kritik 3 kural (bunları asla ihlal etme)

### 1. 15D vs 2D UMAP karışıklığı
2D UMAP koordinatları anomali karar mekanizmasına veya GLOSH hesabına **kesinlikle girmez**. Anomali ve
yoğunluk tespiti tamamen 15D UMAP ara uzayında gerçekleşir. Bir fonksiyon her ikisini de kullanıyorsa
mutlaka hangi UMAP çıktısının hangi amaçla kullanıldığını (görselleştirme mi, karar mı) netleştir.

### 2. GLOSH ve risk_skoru birer olasılık değildir
- GLOSH `[0,1]` aralığında ama kalibre edilmiş bir olasılık değildir; `clusterer.outlier_scores_`
  doğrudan kullanılır, ek normalizasyon yapılmaz.
- `risk_skoru` de olasılık değildir — üç kanıt katmanının (kNN impurity, semantik fark, GLOSH) sezgisel
  ağırlıklı birleşimiyle türetilen bir "Manuel İnceleme Önceliği" metriğidir. `knn_baskinlik` bu formüle
  girmez.
- Kod yorumlarında, değişken isimlerinde, UI metninde veya raporlarda bu skorları "olasılık" / "kesinlik"
  olarak sunma. Doğru çerçeve: "manuel inceleme için yüksek öncelikli aday".

### 3. İki aşamalı (coarse-to-fine) eşik mantığı bir çelişki değildir
`sim_fark > 0.08` (ön aday, geniş tarama) ile `label_sim_fark >= 0.09` (final kabul, sıkı eşik) aynı
metriğin iki farklı aşamadaki farklı kullanımıdır. Biri diğerine "eşitlenmemeli" — bu kasıtlı bir tasarım.

## Formüller (tam sabitler `params.md`'de)

**Ön aday kararı:**
```python
supheli_mi = 1 if (
    ortak_derinlik <= 1
    and knn_impurity >= 0.50
    and sim_fark > 0.08
    and knn_onayliyor_mu == 1
    and (knn_baskinlik >= 0.30 or glosh_scores[i] > 0.70)
) else 0
```

**Risk skoru:**
```python
risk_skoru = knn_impurity * 0.40 + min(max(label_sim_fark, 0), 1) * 0.35 + glosh_val * 0.25
```

## Mevcut üretim funnel'ı (referans, değişiklik sonrası karşılaştırma için)
```
20.902 Makale → HDBSCAN: 11.584 kümeli (293 küme) / 9.318 noise
  → şüpheli_mi: 705 ön aday
  → label_sim_fark >= 0.09: 642 aday
  → final filtreler: 388 nihai anomali
```

## Legacy K-Means
`clustering/kmeans/` üretim hattının bir parçası DEĞİL — dashboard'da arşiv/karşılaştırma amaçlı
tutuluyor. Buradaki değişiklikler HDBSCAN hattını etkilemez ve etkilememeli.

## Değişiklik yaparken checklist
1. Hangi sabiti/eşiği değiştiriyorsun, `params.md`'deki hangi satıra karşılık geliyor?
2. Bu değişiklik `results/hdbscan_tum_makaleler.csv` ve `results/hdbscan_anomaliler.csv`'nin yeniden
   üretilmesini gerektiriyor mu?
3. Funnel sayıları (705 / 642 / 388) değişecek mi — kullanıcıya bunu bekleyip beklemediğini sor.
4. `reviewer` ajanının kontrol listesindeki CRITICAL maddelerle çelişiyor mu?
