# trdizin-clustering için 5 Skill

Ajanların kullandığı skill'lerin gerçek hali. Her skill = bir klasör + `SKILL.md` (zenginlerinde ek
referans dosyası). `selmakcby/claude-agents-skills` deposundaki `tdd` / `ui-ux-pro-max` / `code-review`
skill örneklerinin bu ML projesine uyarlanmış hali.

## Klasör yapısı

```
~/.claude/skills/
├── trdizin-data-pipeline/
│   └── SKILL.md                    ← basit skill · TR Dizin fetch + embedding_text + MPNet
│
├── hdbscan-anomaly-pipeline/       ← zengin skill (en kritik olan)
│   ├── SKILL.md                    ← ana talimat: pipeline sırası + 3 sert kural
│   └── params.md                   ← referans · tüm sayısal sabitler/eşikler/ağırlıklar
│
├── dashboard-flask-plotly/
│   └── SKILL.md                    ← basit skill · Flask API + Plotly WebGL konvansiyonları
│
├── methodology-doc-writer/
│   └── SKILL.md                    ← basit skill · METHODOLOGY_AND_HANDOFF.md üslubu + yasak dil listesi
│
└── docker-gpu-ops/
    └── SKILL.md                    ← basit skill · docker compose / GPU / yedekleme komutları
```

## Kurulum

```bash
# Tüm skill'ler:
cp -r skills/*/ ~/.claude/skills/

# Tek tek de kurulabilir, örn:
cp -r skills/hdbscan-anomaly-pipeline ~/.claude/skills/
```

## Doğrulama

Claude Code'da skill'i çağırmak için:

```
/trdizin-data-pipeline
/hdbscan-anomaly-pipeline
/dashboard-flask-plotly
/methodology-doc-writer
/docker-gpu-ops
```

Ama genelde elle çağırmana gerek yok — ilgili ajan (`pipeline-agent`, `clustering-agent`,
`dashboard-agent`, `reviewer`) görev tanımına göre otomatik olarak doğru skill'i kullanır, çünkü her
`SKILL.md`'nin `description` alanı "ne zaman tetikleneceğini" tarif ediyor.

## Ajan-skill eşleşmesi

| Ajan | Kullandığı Skill'ler |
|---|---|
| planner | (skill kullanmaz, sadece okur) |
| pipeline-agent | `/trdizin-data-pipeline`, `/docker-gpu-ops` |
| clustering-agent | `/hdbscan-anomaly-pipeline` |
| dashboard-agent | `/dashboard-flask-plotly`, `/methodology-doc-writer` |
| reviewer | `/hdbscan-anomaly-pipeline`, `/methodology-doc-writer` |

## Neden `hdbscan-anomaly-pipeline` "zengin" skill?

Bu proje için en hataya açık alan burası: GLOSH'un olasılık sanılması, risk_skoru'na `knn_baskinlik`in
sızması, 2D UMAP'in karar mantığına karışması gibi hatalar sessizce metodolojiyi bozar. Bu yüzden tüm
sabitler ayrı bir `params.md` referans dosyasında tutuluyor — `SKILL.md` "hangi kuralı neden" anlatıyor,
`params.md` "tam sayı ne" sorusuna cevap veriyor. Diğer 4 skill tek dosyalık basit skill olarak yeterli.
