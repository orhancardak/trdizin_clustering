# TR Dizin Clustering Projesi — Güvenli Refaktör Rehberi

Bu rehber, `trdizin-clustering` projesine özel olarak hazırlandı. Amaç basit: **çalışan hiçbir şeyi bozmadan**, küçük ve geri alınabilir adımlarla kodu temizlemek. Panik yok, acele yok. Her adımda "bir şey bozulursa nasıl geri dönerim?" sorusunun cevabı elinde olacak.

---

## 1. Hazırlık ve Güvenlik Adımları

### Önce mevcut durumu koru
Projende zaten bir git geçmişi var (`git log` ile 20+ commit görülüyor), bu iyi bir başlangıç. Ama refaktöre başlamadan önce:

```bash
git status          # bekleyen değişiklik var mı, temiz mi?
git checkout main
git pull             # en güncel hali al
git checkout -b refactor/kmeans-cleanup   # YENİ bir branch aç
```

**Kural: `main` branch'ine asla doğrudan dokunma.** Her refaktör görevi için ayrı, açıklayıcı isimli bir branch aç (`refactor/dashboard-app`, `refactor/remove-duplicate-kmeans-scripts` gibi). Bir şey ters giderse tek yapman gereken branch'i silmek; `main` hep güvende kalır.

### Çalışan sistemin bir "anlık görüntüsünü" al
Bu proje bir ML pipeline'ı — yani "doğru çalışıyor" demek sadece "kod hata vermiyor" değil, **çıktıların aynı kalması** demek. Refaktöre başlamadan önce:

- `results/` klasöründeki mevcut CSV dosyalarını (`hdbscan_tum_makaleler.csv`, `seeded_cluster_assignments.csv` vb.) bir kenara kopyala (örn. `results_BASELINE_BEFORE_REFACTOR/`). Refaktör sonrası aynı scripti çalıştırıp çıktıyı bu baseline ile karşılaştıracaksın.
- Dashboard'ı (`docker compose up -d --build`) bir kere çalıştırıp ekran görüntüleri al veya hangi sayfaların/özelliklerin çalıştığını not et. "Refaktör öncesi çalışıyordu" diyebilmen için somut bir referans lazım.

### İlk commit'lerini nasıl planlamalısın?
En sık yapılan hata: "hem temizlik hem yeni özellik" gibi karışık commit'ler atmak. Bunun yerine:

- **Her commit tek bir şey yapsın.** "Fonksiyon adlarını düzelt" ayrı commit, "tekrarlanan kodu fonksiyona çıkar" ayrı commit.
- Commit mesajını şu formatta yaz: `refactor: <ne yaptın>` — örn. `refactor: kmeans klasöründeki tekrar eden veri yükleme kodunu tek fonksiyona topla`
- **Davranış değiştiren hiçbir şeyi refaktör commit'ine karıştırma.** Refaktör = kodun *dışarıdan görünen davranışı aynı kalırken* iç yapısının iyileşmesi. Bir bug fark edersen bile onu ayrı bir commit'te, ayrı olarak yap.

Bu sayede bir şey bozulduğunda `git bisect` ile veya sadece commit geçmişine bakarak "hangi adımda bozuldu" sorusuna dakikalar içinde cevap bulabilirsin.

---

## 2. Analiz Aşaması: Sorunlu Yerleri Nasıl Tespit Ederim?

Projene baktığımda gözüme çarpan somut "code smell" (kod kokusu) örnekleri var — bunlar senin için iyi bir başlangıç noktası:

### a) `clustering/kmeans/archive/` klasörü — 18 dosya
Bu klasörde `multilabel_cosine.py`, `multilabel_seeded_kmeans.py`, `balanced_adaptive_kmeans.py`, `tuned_adaptive_kmeans.py`, `gap_adaptive_kmeans.py` gibi birbirine çok benzeyen isimlerde **18 ayrı script** var. Bu klasik bir "kopyala-yapıştır-değiştir" kokusu: muhtemelen bir fikri denemek için scripti kopyalayıp küçük değişiklikler yapılmış, sonuç olarak aynı mantık onlarca kez tekrarlanmış.

**Bu, refaktör için en düşük riskli ve en yüksek etkili başlangıç noktasıdır** çünkü `archive/` klasöründeki dosyalar muhtemelen aktif pipeline tarafından import edilmiyor (isimden anlaşılıyor: arşiv). Önce bunu doğrula:

```bash
grep -rn "from clustering.kmeans.archive" --include="*.py" .
grep -rn "import archive" --include="*.py" .
```

Hiçbir yerden import edilmiyorsa, bu klasör "ölü kod" (dead code) olabilir — silmek bile bir refaktördür (ama önce ekip/mentörle teyit et, belki referans olarak tutuluyordur).

### b) Aktif pipeline dosyaları arasında tekrar
`adaptive_multilabel_kmeans.py`, `adaptive_label_count_v2.py`, `adaptive_label_count_v2_20k.py`, `final_kmeans_fixed_and_relabel.py` gibi dosyalar muhtemelen ortak adımları (veri yükleme, embedding okuma, mesafe hesaplama) tekrar tekrar yazıyor. Bunu tespit etmenin pratik yolu:

1. İki dosyayı yan yana aç.
2. İlk 20-30 satıra bak (genelde import + veri yükleme burada olur).
3. Neredeyse birebir aynıysa, bu bir "tekrar eden kod" kokusudur → ortak bir yardımcı modüle (`clustering/kmeans/common.py` gibi) çıkarılabilir.

### c) Nereden başlamalıyım? Öncelik sırası:
1. **Hiç riski olmayanlar:** Kullanılmayan/arşiv dosyalar, yorum satırı haline getirilmiş kod parçaları.
2. **Düşük risk, yüksek fayda:** İsimlendirme düzeltmeleri, tekrar eden kodun fonksiyona çıkarılması (davranış değişmiyor).
3. **Orta risk:** Büyük fonksiyonları küçük fonksiyonlara bölmek.
4. **Yüksek risk — en son, ve mentörünle konuşmadan yapma:** `dashboard/app.py` gibi canlı sistemde çalışan, veritabanı/API bağlantısı olan dosyaların mimari değişiklikleri.

Kısacası: **"kullanılmıyor mu / izole mi" sorusunun cevabı evetse, orası güvenli başlangıç noktandır.**

---

## 3. Adım Adım Uygulama Planı

Refaktörde doğru sıralama, riski en aza indirir. Önerilen sıra (kolaydan zora):

| Sıra | Adım | Neden bu sırada? |
|---|---|---|
| 1 | **İsimlendirme** (`df1`, `x`, `tmp` → anlamlı isimler) | Davranışı asla değiştirmez, en güvenli adım |
| 2 | **Ölü kod / kullanılmayan importları temizleme** | Silinen şey zaten çalışmıyordu, riski çok düşük |
| 3 | **Tekrar eden kodu fonksiyona/modüle çıkarma** | Mantığı taşıyorsun, yaratmıyorsun — dikkatli olursan davranış aynı kalır |
| 4 | **Uzun fonksiyonları bölme** (tek fonksiyon 100+ satırsa) | Artık kodu daha iyi anladın, güvenle bölebilirsin |
| 5 | **Dosya/klasör yapısını (mimari) değiştirme** | En riskli — importlar, path'ler, Docker volume'leri etkilenebilir |

### Her adımda "sistemi bozmadım" nasıl anlarım?
Bu proje için altın kural: **her küçük değişiklikten sonra ilgili scripti/sayfayı gerçekten çalıştır, sadece "syntax hatası yok" ile yetinme.**

Pratik döngü:
1. Küçük bir değişiklik yap (örn. tek bir fonksiyonu çıkar).
2. İlgili scripti çalıştır (örn. `python clustering/kmeans/adaptive_label_count_v2.py`).
3. Çıktıyı (CSV, log, dashboard ekranı) Bölüm 1'de aldığın baseline ile karşılaştır.
4. Aynıysa → commit at. Farklıysa → hemen geri al (`git checkout -- dosya.py`) ve neyin değiştiğini anla.

**Asla "birkaç dosyayı birden değiştirip sonra hepsini test edeyim" deme.** Bir seferde bir dosya, bir seferde bir mantıksal değişiklik.

---

## 4. Test ve Kontrol: Değişikliğin Doğru Çalıştığını Nasıl Doğrularım?

Projede şu an klasik anlamda otomatik test (pytest gibi) görünmüyor — `test_max_label_count.py` ve `test_all_20k_kmeans.py` aslında birer "test" scripti değil, deneme scriptleri gibi duruyor. Bu senin için hem bir zorluk hem bir fırsat.

### Otomatik doğrulama olmadan nasıl güvenli olurum?
**"Karşılaştırmalı doğrulama" (diff testing) tekniğini kullan** — bu ML projeleri için endüstri standardıdır:

1. Refaktörden **önce** scripti çalıştır, çıktıyı `output_before.csv` olarak kaydet.
2. Refaktörden **sonra** aynı scripti çalıştır, `output_after.csv` olarak kaydet.
3. İkisini karşılaştır:
   ```python
   import pandas as pd
   before = pd.read_csv("output_before.csv")
   after = pd.read_csv("output_after.csv")
   print(before.equals(after))  # True olmalı
   # Farklıysa hangi satırların değiştiğini bul:
   diff = before.compare(after)
   print(diff)
   ```
4. `True` çıkmıyorsa refaktörün davranışı değiştirmiş demektir — bu ciddi bir uyarı, geri dönüp bak.

### Dashboard için manuel kontrol listesi
`dashboard/app.py` gibi Flask uygulamasında değişiklik yaptıysan:
- `docker compose up -d --build` ile yeniden başlat.
- Ana sayfa, HDBSCAN görünümü, K-Means görünümü, anomali tespiti sayfası gibi her ana ekranı elle gez.
- Tarayıcı konsolunda (F12) kırmızı hata var mı bak.
- Bir makale detayına tıkla, filtre uygula — "önce nasıl davranıyordu" ile karşılaştır.

### Basit bir "smoke test" (duman testi) eklemeyi düşün
Zaman kalırsa, en kritik 2-3 fonksiyon için 5 satırlık basit testler yazmak bile büyük fark yaratır:
```python
# örn: clustering/kmeans/tests/test_smoke.py
def test_adaptive_label_count_runs_without_error():
    result = adaptive_label_count(sample_embeddings)
    assert result is not None
    assert len(result) > 0
```
Bunu mentörüne "ekleyebilir miyim?" diye sorman iyi bir izlenim bırakır — proaktif davranmış olursun.

---

## 5. Senior Code Review Öncesi Kontrol Listesi

Değişiklikleri sunmadan önce şunları kontrol et — bu liste, kıdemli bir yazılımcının bakacağı ilk şeylerdir:

- [ ] **Branch temiz mi?** `git log --oneline` ile commit geçmişini gözden geçir; anlamsız commit'ler varsa (`wip`, `deneme`, `asdf`) `git rebase -i` ile temizle veya en azından mentörüne "bunlar deneme commit'leri" diye açıkla.
- [ ] **Diff'i baştan sona kendin okudun mu?** `git diff main...refactor/branch-adin` çalıştır ve her satırı oku. Kendi gözünle görmediğin bir değişikliği başkasına gösterme.
- [ ] **Davranış gerçekten aynı mı kaldı?** Bölüm 4'teki "before/after" karşılaştırmasının sonucunu (ekran görüntüsü veya diff çıktısı) hazır tut — senior'a "işte kanıtı, çıktılar birebir aynı" diyebilmelisin.
- [ ] **Gereksiz dosya/değişiklik sızmış mı?** `.DS_Store`, geçici test dosyaları, IDE ayar dosyaları (`.vscode/`, `__pycache__/`) commit'e karışmamalı — `.gitignore`'a bak.
- [ ] **Commit mesajları anlamlı mı?** Her commit'in ne yaptığı, mesajı okuyunca anlaşılıyor mu?
- [ ] **Büyük veri/model dosyası commit'lenmiş mi?** `results/`, `models/`, `embeddings/`, `data/` gibi klasörlerdeki CSV/model dosyalarını yanlışlıkla commit etmediğinden emin ol — bunlar genelde `.gitignore` ile hariç tutulmalı.
- [ ] **PR açıklaması var mı?** Kısa bir açıklama yaz: *ne değişti, neden değişti, nasıl test ettim*. Bu üç cümle bile büyük fark yaratır.
- [ ] **"Neden" sorusuna cevabın hazır mı?** Senior sana "neden bu fonksiyonu buraya taşıdın?" diye sorabilir — her değişikliğin arkasındaki mantığı bir cümlede özetleyebilmelisin.

---

## Kısa Özet — Aklında Kalsın

1. **Branch aç, `main`'e dokunma.**
2. **Önce baseline (mevcut çıktı) al, sonra dokun.**
3. **En kolaydan başla:** isimlendirme → ölü kod → tekrar eden kod → büyük fonksiyonlar → mimari.
4. **Her küçük adımdan sonra gerçekten çalıştır ve karşılaştır.**
5. **Bir commit = bir amaç. Refaktörü bug fix'le karıştırma.**
6. **Review'e gitmeden önce diff'ini kendin oku.**

Unutma: kıdemli yazılımcıların da işlerini bozduğu olur. Fark, onların bunu **küçük adımlarla, geri alınabilir şekilde ve kanıtlayarak** yapmasıdır. Bu rehberi izlersen sen de aynısını yapıyor olacaksın.
