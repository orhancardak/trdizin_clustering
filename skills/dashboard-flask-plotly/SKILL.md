---
name: dashboard-flask-plotly
description: dashboard/app.py, dashboard/data_loader.py, templates/*.html, static/js/main.js veya static/css/style.css ile ilgili her görevde kullan. Flask REST API, Plotly WebGL scatter ve explainability kartlarıyla ilgili konvansiyonları içerir.
---

# Dashboard (Flask + Plotly) Skill'i

## Ne zaman aktif olunacak
`dashboard/` klasöründe yeni bir endpoint, grafik, filtre veya modal eklenirken; ya da anomali/risk
skorunun panelde nasıl sunulacağı sorulduğunda.

## Mimari
- **Backend:** `app.py` — Flask, port 5001. Bilinen uç noktalar: `/api/anomalies`, `/api/plot`,
  `/api/article`. Yeni uç nokta eklerken aynı `/api/*` konvansiyonunu ve JSON response şeklini koru.
- **Veri katmanı:** `data_loader.py` — CSV'leri (`results/hdbscan_tum_makaleler.csv`,
  `results/hdbscan_anomaliler.csv`) uygulama açılışında bir kez okuyup bellekte tutan lazy-cache deseni.
  Her istekte diskten okuma ekleme.
- **`why_flagged` üretimi:** `data_loader.py` içinde, bir makalenin neden aday olduğunu (hangi koşullar
  tetiklendi: ortak disiplin, knn_impurity, sim_fark, glosh) insan-okunabilir cümleye çeviren mantık.
  Yeni bir sinyal eklersen bu üretim mantığını da güncelle.
- **Frontend:** `templates/index.html` (ana panel), `templates/kmeans.html` (legacy K-Means arşivi),
  `static/js/main.js` (Plotly `scattergl` — WebGL, büyük nokta sayısı için zorunlu, normal `scatter`'a
  düşürme), `static/css/style.css` (TÜBİTAK kurumsal nötr palet).

## Zorunlu içerik: metodolojik uyarı
Panelde şu (veya anlamca eşdeğer) uyarı metni bulunmalı ve kaldırılmamalı:

> "Bu çıktı otomatik bir yanlış etiket kararı değildir. Sistem, makaleyi semantik ve yerel komşuluk
> sinyallerine göre manuel inceleme için aday olarak işaretler."

## Gösterge/filtre kuralları
- Anomali tablosunda TP-1 (Farklı Ana Disiplin, `ortak_agac_derinligi==0`) ve TP-2 (Alt Alan Uyuşmazlığı,
  `==1`) ayrımı korunmalı — bunları tek bir "anomali" etiketinde birleştirme.
- GLOSH ve risk_skoru sayısal olarak gösterilebilir ama yanına "olasılık" ibaresi veya % işareti
  "kesinlik" anlamında eklenmemeli. "Öncelik skoru" / "risk skoru" gibi nötr etiketler kullan.
- Makale detay modalında: başlık, özet, mevcut taksonomi yolu, önerilen taksonomi yolu, kNN komşuları ve
  `why_flagged` metni birlikte gösterilmeli — sadece tek bir sayı değil.

## K-Means (legacy) sayfası
`templates/kmeans.html`: Seeded K-Means'in gerçek/tahmin edilen çoklu etiket karşılaştırması, F1 skorları,
Exact Match oranı. Bu sayfa **üretim HDBSCAN akışından bağımsız bir arşiv** — yeni özellik eklerken HDBSCAN
verisiyle karıştırma.

## Performans
- Plotly grafiklerinde 11k+ nokta olabileceğinden `scattergl` kullan, `mode='markers'`, gereksiz hover
  bilgisini client-side'da lazy yükle.
- `/api/anomalies` gibi uç noktalarda sayfalama (pagination) veya en azından üst limit düşün; 388 satır
  küçük ama `hdbscan_tum_makaleler.csv` (20.902 satır, ~43MB) tam olarak her istekte serialize edilmemeli.
