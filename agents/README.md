# trdizin-clustering için 5 Ajan

Bu klasör `trdizin-clustering` projesine özel 5 Claude Code alt-ajanının gerçek hali. Her biri ayrı bir
markdown dosyası, `selmakcby/claude-agents-skills` deposundaki 4-ajan mimarisi (planner / ui-agent /
builder / reviewer) örnek alınarak bu ML projesine uyarlanmıştır.

## Klasör yapısı

```
~/.claude/agents/
├── planner.md            ← Görevi data_pipeline / clustering / dashboard katmanlarına böler (opus)
├── pipeline-agent.md     ← TR Dizin veri çekme, embedding üretimi, Docker/GPU (sonnet)
├── clustering-agent.md   ← HDBSCAN/GLOSH üretim hattı + legacy K-Means (sonnet)
├── dashboard-agent.md    ← Flask + Plotly dashboard (sonnet)
└── reviewer.md           ← Kod + metodoloji denetimi (sonnet)
```

## Kurulum

```bash
mkdir -p ~/.claude/agents
cp *.md ~/.claude/agents/
```

Doğrulama — Claude Code'da:

```
/agents
```

5 ajanın listede göründüğünü göreceksin.

## Kullanım akışı

```
kullanıcı: "HDBSCAN min_cluster_size'ı 15 yapıp anomali sayısının nasıl değiştiğini raporla"
    ↓
ANA CLAUDE (orchestrator)
    ↓ (Task tool ile sırayla çağırıyor)
    ├─→ planner            → adımlara böler, reviewer için kriter listesi verir
    ├─→ clustering-agent   → outlier_detector.py / run_hdbscan_pipeline.py'yi değiştirir, küçük örneklemde test eder
    └─→ reviewer           → CRITICAL metodoloji kontrolü yapar (risk_skoru formülü, GLOSH olasılık değil vb.)
```

Veri toplama + embedding gerektiren bir görevde `pipeline-agent`, dashboard/UI gerektiren bir görevde
`dashboard-agent` devreye girer. Orchestrator (Ana Claude) hangi ajanın gerektiğine `description` alanına
bakarak karar verir.

## Model seçimleri

| Ajan | Model | Neden |
|---|---|---|
| planner | opus | En derin akıl yürütme — hangi katmana ne düşeceğine karar veriyor |
| pipeline-agent | sonnet | Veri işleme + Docker/Bash — dengeli |
| clustering-agent | sonnet | ML kodu + sayısal doğrulama — dengeli |
| dashboard-agent | sonnet | Flask/JS/HTML — dengeli |
| reviewer | sonnet | Detaylı inceleme — dengeli |

## Araç izinleri (güç paylaşımı)

| Ajan | Okuma | Yazma | Bash |
|---|---|---|---|
| planner | ✓ | ✗ | ✗ |
| pipeline-agent | ✓ | ✓ | ✓ |
| clustering-agent | ✓ | ✓ | ✓ |
| dashboard-agent | ✓ | ✓ | ✗ (Flask/JS'de komut çalıştırmaya gerek yok) |
| reviewer | ✓ | ✗ | ✓ (git diff, statik kontrol için) |

Planner sadece okur. Reviewer inceleyebilir ama yazamaz. Builder ajanları (pipeline/clustering/dashboard)
yazabilir ama review edemez.

## Önemli: ajanlar birbirini çağırmıyor

Hiçbirinde `Task` aracı yok. Bu bilinçli bir seçim:
- Ajanlar birbirini çağıramıyor (alt-ajan spawn edemez)
- Tüm koordinasyon Ana Claude üzerinden geçiyor
- Context fragmentasyonu olmuyor, debug kolay

## Skills

Ajanlar bu skill'leri kullanıyor (ayrı kurulum, `~/.claude/skills/` altında — bkz. `../skills/README.md`):

- `/trdizin-data-pipeline` — pipeline-agent için
- `/docker-gpu-ops` — pipeline-agent için
- `/hdbscan-anomaly-pipeline` — clustering-agent ve reviewer için
- `/dashboard-flask-plotly` — dashboard-agent için
- `/methodology-doc-writer` — pipeline-agent, dashboard-agent ve reviewer için (METHODOLOGY_AND_HANDOFF.md ile tutarlı yazım)
