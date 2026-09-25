---
name: docker-gpu-ops
description: docker-compose.yml, Dockerfile, Caddyfile ile ilgili görevlerde veya servisleri ayağa kaldırma/loglama/yedekleme gibi operasyonel komutlar gerektiğinde kullan. GPU/CUDA gereksinimleriyle ilgili sorularda da bu skill'e bak.
---

# Docker + GPU Operasyon Skill'i

## Ne zaman aktif olunacak
`docker-compose.yml`, `Dockerfile`, `Caddyfile` değiştirilirken; servis başlatma/durdurma/log
takibi/yedekleme gibi operasyonel bir komut istendiğinde.

## Servisler
| Servis | Port (host→container) | Görev |
|---|---|---|
| app | 5001 | Python 3.12 + PyTorch (CUDA 12.6) Flask dashboard, `dashboard/app.py` |
| postgres | 5434 → 5432 | PostgreSQL 16, db `trdizin_clustering_db`, volume `postgres_data` |

## GPU gereksinimi
Embedding üretimi (`generate_mpnet_embeddings_20k.py`) ve UMAP boyut indirgeme adımlarında donanım
hızlandırması gerekir:
- Sunucuda `nvidia-container-toolkit` kurulu olmalı
- Docker'ın GPU'ya erişebildiğinden emin olunmalı
- `docker-compose.yml` içinde `gpus: all` tanımlı olmalı — bunu kaldırma, kaldırırsan embedding üretimi
  CPU'da çok yavaşlar veya bazı kütüphaneler hata verir

## Temel komutlar
```bash
# İlk kurulum / servisleri ayağa kaldır
docker compose up -d --build

# Durum ve health check
docker compose ps

# Logları takip et
docker compose logs -f app

# Container içine gir
docker exec -it trdizin_clustering_app bash

# Pipeline'ı container içinde sırayla çalıştır
python data_pipeline/fetch_balanced_trdizin.py
python data_pipeline/generate_mpnet_embeddings_20k.py
python data_pipeline/build_embedding_index.py
python clustering/hdbscan/run_hdbscan_pipeline.py
```

## Yedekleme
```bash
# Veri, embedding ve sonuç çıktıları
tar -czvf trdizin_clustering_backup_$(date +%F).tar.gz data/ embeddings/ results/

# PostgreSQL yedeği
docker exec trdizin_clustering_postgres pg_dump -U postgres trdizin_clustering_db > trdizin_db_$(date +%F).sql
```

## Dikkat
- `docker-compose.yml`'de port değişikliği yaparsan README.md'deki erişim adreslerini de güncellemeyi
  öner (5001/5434 birçok yerde referans veriliyor).
- Yeni bir servis eklerken (ör. Qdrant, Caddy reverse proxy) mevcut healthcheck deseniyle tutarlı kal.
- Büyük dosyalar (`.npy` ~64MB, `hdbscan_tum_makaleler.csv` ~43MB, `balanced_articles.csv` ~78MB) image
  içine gömülmemeli — volume mount ile bağlanmalı, yoksa image boyutu ve build süresi patlar.
