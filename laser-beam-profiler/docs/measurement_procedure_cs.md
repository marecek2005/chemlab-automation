# Postup experimentu — low-cost laser beam profiler (SVK)

**Účel:** praktický lab postup (ne teorie). Změřit profil zeleného laseru kolem fokusu čočky → Gaussův fit, w₀, zᵣ, divergence, odhad M² (ISO-inspired).

**Norma:** principy **ISO 11146:1999** (+ digesty). Aktuální **ISO 11146-1:2021** ověřit v NTK. Detailní text: `protokol_experimentu_kompletni.md`.

**Aparatura**
| Kus | Model / poznámka |
|-----|------------------|
| Laser | zelený laserový modul ~**532 nm** (typ potvrdit ze štítku); napájení dle lab |
| Čočka | Ø2″ plano-convex **f = 100 mm** (≈ LA1050), 3D-tištěný držák |
| Kamera | Thorlabs Zelux **CS165MU/M** (pixel **3,45 µm**, 1440×1080) |
| Stolek | Thorlabs **PT1/M**, 25 mm, dílek **10 µm** |
| Attenuace | ND **NEK01 na kameře** |
| SW | ThorCam + jednoduchý Python (Mac vývoj / Windows lab) |

**Omezení pasu:** očekávaný **2w₀ ≈ 5–6 px** (w₀ ≈ 2,5–3 px při w_in ≈ 1,75 mm, f = 100 mm) → pod doporučením ≥10–20 px. M² jen jako **odhad**.

---

## 0. Bezpečnost

1. Nikdy do očí ani odrazem (třída 3R / 2 dle štítku).
2. Brýle dle λ, pokud lab má; paprsek jen do stínítka / kamery.
3. Laser zapínat až po hrubém ustavení; vypínač v dosahu.
4. ND na kameře **před** live view.
5. Deník: operátor, datum, místnost, **foto štítku**.
6. **Warm-up 15–30 min** před měřením (ISO 11146:1999 §7.1 uvádí ≥1 h, pokud výrobce nestanoví jinak).

---

## 1. Příprava

1. Osa: laser → čočka → kamera na PT1/M.
2. Pixel → µm: **3,45 µm/px**.
3. Složka `surova_data/YYYY-MM-DD_runN/` + log (λ, f, ND OD, definice z = 0).

---

## 2. Zarovnání a ND

1. Silný ND (OD ~3–4); spot ve středu čipu; bez saturace.
2. I největší spot ve scanu **neclipuje** okraj (< ~1 % výkonu).

---

## 3. Nalezení pasu

1. Projet zdvih, najít minimum; zapsat zᵥᵢₛ.
2. Odhad 2w₀ v px — pokud ≤ ~8 px: VAROVÁNÍ / mitigace.
3. **Odhad:** w₀ ≈ λ f / (π w_in) → w₀ ≈ 2,8 px, **2w₀ ≈ 5–6 px** (w_in ≈ 1,75 mm).

---

## 4. Mřížka z (ISO-styl)

Odhad (M² ≈ 1): zᵣ ≈ π w₀² / λ ≈ 0,6 mm; 2 zᵣ ≈ 1,2 mm. **25 mm zdvih stačí.**

- **≥ 10** pozic celkem;
- **≥ 5** v |z − z₀| ≤ zᵣ (obě strany pasu);
- Far field **symetricky:** ideálně **≥ 5 před a ≥ 5 za** pasem s |z − z₀| ≥ 2 zᵣ.

**Backlash PT1/M:** každou z najížděj **z jednoho směru**; při přejetí couvni ≥ 1 mm a znovu najedi.

Nejdřív hrubý scan po 1 mm → fit → doplň jemné body kolem pasu. Eliptický svazek: X a Y zvlášť.

---

## 5. Akvizice na každém z

1. Mikrometr z jednoho směru; zapiš z.
2. Peak bez saturace (30–70 % ADC).
3. **≥ 5** (lépe 10) framů: `zXXXXXum_frameK.tif`.
4. Background (laser zakrytý), stejná expozice.
5. **ND během z-scanu NEMĚŇ** (posun fokusu Δz ≈ t(1 − 1/n) ~ zᵣ). Intenzitu řeš **expozicí**, ne výměnou ND.

---

## 6. Log

datum, operátor, laser (štítek), f, ND, z = 0, pro každý bod: z, expo, gain, soubory; saturace/clip/elipsa.

---

## 7. Vyhodnocení (Python)

1. Snímky → **float64** → odečti background (**ne uint16**) → průměr framů.
2. **Primárně Gauss:** w = 2σ (1/e²); fit w(z) → w₀, z₀, zᵣ; θ ≈ w₀/zᵣ.
3. Kontrola: **π w₀² / zᵣ = M² · λ** (ne čisté λ).
4. **Volitelně D4σ/M²:** adaptivní ROI (~3–4× průměr, iterace) — **ne celý čip**; wₑff = √(2(σₓ²+σᵧ²)).
   - **w² = a + bz + cz²:** w₀ = √(4ac−b²)/(2√c), z₀ = −b/(2c), zᵣ = √(4ac−b²)/(2c), θ = √c, M² = (π/(2λ))√(4ac−b²);
   - **d² = a + bz + cz²:** θ = √c/2, M² = (π/(8λ))√(4ac−b²). **Pozor na faktor 4.**
5. Caveat 2w₀ ≈ 5–6 px. **Langer:** Gauss, bez D4σ, často 1 frame/z. **Bonnett:** bez M².
6. Vliv čočky: w₀ ≈ λ f / (π w_in).

---

## 8. Mitigace malého pasu

Přijmout limit + větší nejistota; nebo upravit vzdálenost laser–čočka (zapsat); později delší f / relay.

---

## 9. Konec

Laser VYP; data zálohovat; log kompletní.

---

## Measured quantities (EN — for SVK Methods)

- Beam intensity profiles I(x,y) at discrete axial positions z through the focus of an f = 100 mm plano-convex lens
- 1/e² beam radii wₓ(z), wᵧ(z) from Gaussian fits (primary)
- Optional ISO-style second-moment diameters dσₓ(z), dσᵧ(z) (D4σ) with adaptive ROI
- Effective radius wₑff = √(2(σₓ²+σᵧ²)); waist w₀, location z₀, Rayleigh length zᵣ
- Far-field divergence half-angle θ
- Beam quality estimate M² from hyperbolic fit (ISO-inspired; limited by 2w₀ ≈ 5–6 px)
- Comparison with manufacturer beam size / effect of the focusing lens on the focal spot
