---
name: methodology-doc-writer
description: METHODOLOGY_AND_HANDOFF.md dosyasını güncellerken, yeni bir bölüm eklerken veya başka bir dokümanı bu projenin metodoloji dokümanıyla aynı üslup/yapıda yazarken kullan. Ayrıca reviewer'ın "yasak dil" kontrolü için terminoloji referansı olarak da kullanılır.
---

# Metodoloji Dokümanı Yazım Skill'i

## Ne zaman aktif olunacak
- `METHODOLOGY_AND_HANDOFF.md`'ye yeni bölüm eklenirken veya mevcut bölüm güncellenirken
- Yeni bir metodolojik karar (yeni eşik, yeni sinyal, yeni ablation) dokümante edilirken
- reviewer'ın kod/UI metnindeki dilin dokümanla tutarlı olup olmadığını kontrol etmesi gerektiğinde

## Doküman yapısı ve üslup
1. Başlık: `# TR DİZİN ... SİSTEMİ` + `## Kapsamlı Metodoloji, Deneysel Doğrulama ve Teknik Devir (Handoff) Dokümanı`
2. Versiyon/tarih bloğu (`> **Doküman Versiyonu:**`, `> **Tarih:**`)
3. Numaralı içindekiler tablosu, her bölüm `# N. Başlık` formatında
4. Formüller hem Python kod bloğu hem LaTeX (`$$...$$`) olarak verilir
5. Kritik uyarılar `> **MÜHENDİS İÇİN KRİTİK NOT:**` veya `> **MÜHENDİS İÇİN KRİTİK UYARI:**` blockquote'u
   ile vurgulanır — bunlar rastgele değil, gerçekten downstream'de hata yapılabilecek noktalarda kullanılır
6. Her önemli parametre için "bu metodolojik mi yoksa operasyonel/heuristic mi" ayrımı açıkça yazılır
7. Tablo formatı: parametre/model karşılaştırmaları Markdown tablosu ile, en iyi değer **bold**
8. Dosya/kod yolları her zaman backtick içinde: `` `clustering/hdbscan/outlier_detector.py` ``

## Yasak / kaçınılması gereken ifadeler (terminoloji referansı)
Bu proje bir "otomatik yeniden etiketleme" sistemi DEĞİL. Aşağıdaki ifadeler dokümanda, kodda, UI'de veya
commit mesajlarında kullanılmamalı:
- ❌ "Bu makalenin etiketi kesinlikle yanlıştır"
- ❌ "Model doğru kategoriyi kesin olarak belirlemiştir"
- ❌ "%X olasılıkla yanlış etiketlenmiş" (risk_skoru veya GLOSH için)
- ❌ GLOSH veya risk_skoru'nu "probability" / "confidence" olarak adlandırmak

Doğru çerçeve:
- ✅ "Bu makale semantik olarak mevcut etiketi ve yerel komşuluğuyla tutarsız görünmektedir; bu nedenle
  manuel inceleme için yüksek öncelikli bir adaydır."
- ✅ "Sistem, makalenin gerçek araştırma odağını nihai olarak kanıtlamaz; ... belirgin uyuşmazlıkları
  istatistiksel ve geometrik sinyallerle işaretler."

## Yeni bölüm eklerken checklist
1. Bölüm numarasını içindekiler tablosuna da ekle.
2. Yeni bir parametre/eşikse: değeri, gerekçesini ve metodolojik mi operasyonel mi olduğunu yaz.
3. Yeni bir formülse: hem kod bloğu hem `$$...$$` LaTeX gösterimini ver.
4. Varsa yeni funnel sayılarını (kaç makale bu aşamadan geçti) güncelle ve önceki sayılarla tutarlılığını
   kontrol et.
5. Sınırlılıklar/gelecek çalışmalar bölümüyle çelişip çelişmediğini kontrol et.
