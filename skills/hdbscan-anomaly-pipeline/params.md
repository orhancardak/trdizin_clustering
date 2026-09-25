# Referans: Tüm Sayısal Sabitler (METHODOLOGY_AND_HANDOFF.md kaynaklı)

Bu dosya `hdbscan-anomaly-pipeline` skill'inin ek referansıdır. clustering-agent veya reviewer bir sabiti
değiştirirken/kontrol ederken buraya bakar.

## 15D UMAP (ara temsil — kümeleme için)
| Parametre | Değer | Not |
|---|---|---|
| n_neighbors | 15 | standart manifold dengesi |
| n_components | 15 | kümeleme için ara boyut |
| metric | cosine | açısal anlamsal mesafe |
| random_state | 42 | deterministik |
| low_memory | True | bellek dostu |

## HDBSCAN
| Parametre | Değer | Not |
|---|---|---|
| min_cluster_size | 10 | küme oluşması için asgari çekirdek makale sayısı |
| min_samples | 5 | varsayılan min_cluster_size/2, muhafazakar gürültü toleransı |
| prediction_data | True | GLOSH hesabı için gerekli |

## Qdrant kNN
| Parametre | Değer | Not |
|---|---|---|
| collection | trdizin_articles | |
| named vector | mpnet_v1 | 768D, Cosine |
| search | SearchParams(exact=True) | yaklaşık değil, brute-force |
| limit gönderilen | k+1 = 11 | self-neighbor filtrelenip 10 kalır |
| k (efektif) | 10 | literatürde standart heuristik taban, grid search yapılmamış |

## Ön aday kararı (şüpheli_mi)
| Koşul | Eşik | Gerekçe |
|---|---|---|
| ortak_derinlik | <= 1 | değişiklik yüzeysel olmamalı |
| knn_impurity | >= 0.50 | komşuların en az yarısı farklı etiket |
| sim_fark | > 0.08 | geniş ön eleme eşiği |
| knn_onayliyor_mu | == 1 | komşuluk modele karşı çıkmamalı |
| knn_baskinlik OR glosh | >= 0.30 OR > 0.70 | odak uzlaşması veya yoğunluk anomalisi |

→ 20.902 makaleden **705 ön aday**.

## Final doğrulama filtresi
| Maske | Koşul |
|---|---|
| mask_ana_disiplin | derinlik==0 AND knn_baskinlik>=0.30 |
| mask_alt_alan | derinlik==1 AND (oneri_kategori==knn_oneri OR knn_baskinlik>=0.40) |
| + ortak | label_sim_fark >= 0.09, geçerli başlık (boş/"-"/"None"/"nan" değil, uzunluk>3) |

→ 642 (semantik sıkılaştırma) → **388 final anomali**.

## Risk skoru ağırlıkları
| Bileşen | Ağırlık | Gerekçe |
|---|---|---|
| knn_impurity | 0.40 | en somut lokal hata sinyali |
| label_sim_fark (clip 0-1) | 0.35 | alternatif kategoriye anlamsal çekim |
| glosh | 0.25 | küme yoğunluğundan kopma derecesi |

`knn_baskinlik` risk_skoru formülüne dahil DEĞİLDİR — sadece eşik/konsensüs barajı olarak kullanılır.

## Embedding modeli karşılaştırması (results/embedding_model_comparison.csv)
| Model | Boyut | Silhouette↑ | Davies-Bouldin↓ | Calinski-Harabasz↑ | Singleton↓ | Süre |
|---|---|---|---|---|---|---|
| E5 (multilingual-e5-base) | 768 | -0.0798 | 3.0121 | 11.1333 | 72 | 207.39s |
| BGE-M3 | 1024 | -0.0614 | 3.2194 | 9.2297 | 54 | 716.72s |
| **MPNet-Multilingual** (seçilen) | **768** | **+0.0049** | **2.8914** | **19.9917** | **18** | **169.72s** |

## Taksonomi semantik fark
- `label_sim_fark = best_sim - mevcut_sim`
- `ortak_agac_derinligi == 0`: farklı ana disiplin (en radikal uyuşmazlık)
- `== 1`: alt alan uyuşmazlığı (aynı kök)
- `>= 2`: derin ortaklık, şüpheli sayılmaz
