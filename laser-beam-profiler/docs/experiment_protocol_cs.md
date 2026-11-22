# Kompletní protokol experimentu — low-cost laser beam profiler (SVK)

**Účel dokumentu:** dlouhý „referenční“ protokol, který otevřeš, když ti není něco jasné v krátkém checklistu (`postup_experimentu_2A4.pdf`). Krátký checklist **nemazat** — ten je na stůl.

**Nejde o:** certifikované ISO měření ani plnou teorii (ta je ve `02_svk/fulltext_draft.md` a digestech).

**Právní poznámka k normě:** Pracujeme s principy **ISO 11146:1999** (legální zkrácený sample v `02_svk/papers/iso11146/`) a s veřejnými parafrázemi DataRay / Ophir / Kovalev. Aktuální je **ISO 11146-1:2021** (+ Part 2, TR Part 3) — plné PDF je placené; detaily lze později ověřit v **NTK**. Základní myšlenka (druhé momenty, caustika, M², počet rovin) zůstává stejné rodiny.

---

## 1. Cíl měření (náš setup)

Změřit prostorový profil zeleného diodového laseru kolem ohniska známé čočky a z řady řezů podél osy *z* získat:

| Veličina | Primárně / volitelně | Poznámka |
|----------|----------------------|----------|
| Profil I(x,y) v několika *z* | primárně | ThorCam export |
| Poloměr 1/e² wₓ(z), wᵧ(z) | **primárně** (Gauss) | jako Langer / Bonnett |
| Pas w₀, poloha z₀ | primárně | |
| Rayleighova délka zᵣ | primárně | |
| Divergence θ | primárně | např. θ ≈ w₀/zᵣ |
| M² | **volitelně**, ISO-inspired odhad | jako Langer / Kovalev ISO větev |
| Vliv čočky na fokus | diskuse | porovnání s odhadem w₀ ≈ λ f/(π wᵢₙ) |

**Aparatura (mapování na lab)**

| Prvek | Náš kus | Co z literatury si půjčujeme |
|-------|---------|------------------------------|
| Laser | zelený laserový modul ~**532 nm** (typ potvrdit ze štítku: CPS532 DPSS / C2 / CPS520 / …) | Bonnett: zelený 532 nm; Kovalev: 515,6 nm SHG |
| Čočka | Ø2″ plano-convex **f = 100 mm** (≈ LA1050) | Langer: f ≈ 62,9 mm; Kovalev: f′ = 550 mm |
| Kamera | Zelux **CS165MU/M**, pixel **3,45 µm**, mono | Bonnett: CMOS 1,4 µm; Kovalev: 5,04 µm; Langer: Bayer ~2,79 µm |
| Stolek | **PT1/M**, 25 mm, dílek 10 µm | Bonnett: manuální *z*; Kovalev: lineární platforma |
| ND | **NEK01 na kameře** | Bonnett: step ND před senzorem; ISO: attenuátor nesmí přetvářet relativní profil |
| SW | ThorCam + jednoduchý Python | Bonnett/Kovalev: offline fit |

**Kritický limit:** očekávaný **2w₀ ≈ 5–6 px** (w₀ ≈ 2,5–3 px při w_in ≈ 1,75 mm, f = 100 mm, pixel 3,45 µm) → pod doporučením kamer (~10–20 px na průměr). Gaussův fit může dát sub-pixelovou precizi u TEM₀₀ (Langer), ale **ISO D4σ / M²** bude systematicky nejistý — vždy to napiš do SVK.

---

## 2. Bezpečnost

1. Laser třídy **3R** (~4,5 mW) nebo **2** (CPS532-C2): **nikdy do očí**, pozor na odrazy (stůl, kov, ND pouzdro).
2. Brýle pro 532 nm, pokud je lab má; jinak paprsek jen do stínítka / kamery.
3. ND na kameře **před** zapnutím live view (ochrana senzoru i očí při kontrole).
4. Laser zapínat až po hrubém mechanickém ustavení; vypínač / 5 V napájení v dosahu.
5. Do deníku: operátor, datum, místnost, **foto štítku** laseru (přesný typ ~532 nm potvrdit).
6. **Warm-up:** laser nech běžet **15–30 min** před měřením (stabilizace). ISO 11146:1999 §7.1 uvádí **≥ 1 h**, pokud výrobce nestanoví jinak — u kompaktního diodového/DPSS modulu stačí prakticky 15–30 min; pokud máš čas, klidně déle.
7. Po měření: laser **VYP**, napájení odpojit.

*(Norma ISO 11146 řeší metrologii, ne lab safety — body výše jsou lab praxe + třída laseru.)*

---

## 3. Optické uspořádání

```
[CPS laser] -----> [plano-convex f=100 mm, Ø2"] -----> [ND na kameře] [Zelux na PT1/M]
 z=0 definice dle konvence -------------------------------► rostoucí z (směr šíření)
```

### 3.1 Co říká norma / studie → co děláme my

| Zdroj | Princip | Naše mapování |
|-------|---------|---------------|
| **ISO 11146:1999** §6 | Osa měřicího systému koaxiální s paprskem; clippování &lt; ~1 % výkonu; attenuátory ve středu osy | Zarovnat laser–čočka–kamera; spot vždy na čipu i v dalekém poli |
| **ISO** §6.5–6.6 | Attenuátor / fokus nesmí výrazně měnit relativní profil; chyba fokusu &lt; ~1 % šířky | ND **homogenní** NEK01 na kameře; čočka čistá, kolmá |
| **Langer 2013** | Čočka vytvoří měřitelný fokus; kamera skenuje caustiku | Stejné: f = 100 mm + PT1/M |
| **Bonnett 2021** | Laser fixní, senzor se pohybuje v *z* | Stejné: posouváme **kameru**, ne laser |
| **Kovalev 2022** | CMOS na lineární platformě za fokusující čočkou | Stejná geometrie, kratší f a ruční stolek |

### 3.2 Definice souřadnice *z*

Zvol **jednu** konvenci a drž ji celý run:

- **A)** z = 0 = jeden doraz PT1/M (absolutní mikrometr), nebo 
- **B)** z = 0 = vizuální pas zᵥᵢₛ (relativní).

Zapiš směr: „rostoucí *z* = kamera dál od čočky“ (nebo naopak).

---

## 4. Příprava kamery a ThorCam

1. USB 3, ThorCam; **global shutter**; gain nízko; vypnout auto-exposure, pokud lze.
2. Formát exportu: TIFF/PNG bez ztráty (ne těžká JPEG komprese).
3. Kalibrace délky: **1 px = 3,45 µm** (datasheet Zelux) — zapsat do logu.
4. ROI: ideálně celý čip; pokud ořezáváš, zapiš a ověř, že křídla svazku nejsou useknutá.
5. Lineární režim: peak typicky **30–70 %** plného ADC; **žádný plochý vrchol** (saturace).

**Bonnett 2021** (inspirace nastavení): krátká expozice, gain 1, formát s plnou intenzitou (u nich YUV) — u nás: krátká expo + nízký gain + ND.

---

## 5. Zarovnání (alignment)

1. Nasadit **silný ND** (OD ≈ 3–4).
2. Zapnout laser; live view.
3. Posunem laseru / držáku čočky / kamery dostat spot **doprostřed** senzoru.
4. Projít hrubě *z* a ověřit, že i **největší** spot ve scanu **nepadá z čipu** (ISO: clipping &lt; ~1 %; kontroluj daleké pole, ne pas — DataRay / ISO praxe).
5. Doladit náklon čočky (odrazy, elipsa): cíl je co nejkulatější / stabilní elipsa bez „useknutí“.
6. Pokud je svazek silně eliptický (CPS520): připrav se na **oddělené** wₓ, wᵧ (ISO ∼ple astigmatic / Kovalev X0Z vs Y0Z).

---

## 6. ND a expozice (lineární oblast)

| Zdroj | Poučení | Naše praxe |
|-------|---------|------------|
| ISO 1999 §6.5 | Attenuátor, když výkon překročí lineární rozsah / damage threshold | ND na kameře vždy, když hrozí saturace |
| Bonnett 2021 | OD 0,1–4; pro CMOS často T ≈ 0,1 %; při špatném ND Gauss fit selže | Začni OD 3–4, doladě expo; neměň ND uprostřed caustiky |
| DataRay / Ophir | Offset a šum v křídlech nafouknou druhé momenty | Background mapa + rozumné ROI |

**Postup:**
1. Najdi kombinaci ND + expo, kde profil vypadá hladce Gaussovsky.
2. Zapiš OD hodnoty (např. ND = OD 1 + OD 2).
3. Jednou pro run (nebo při změně ND): pořiď **background** — laser zakrytý / vypnutý, **stejná** expozice a gain.

---

## 7. Nalezení pasu (waist)

**Langer / Bonnett:** vizuálně / skenem najít nejužší místo, pak hustší body kolem něj.

1. Mikrometrem projet celý zdvih 25 mm; sledovat velikost spotu.
2. Zapsat zᵥᵢₛ = poloha minima.
3. Volitelně 3–5 rychlých snímků → hrubý w₀ v pixelech.
4. **Pokud průměr pasu ≤ ~8 px:** 
 - zapsat **VAROVÁNÍ** do logu; 
 - zvážit mitigaci (§14) **před** finální mřížkou; 
 - nebo pokračovat s vědomím, že M² bude jen orientační.

Orientace řádu velikosti (ne cílová hodnota): Langer měl w₀ ≈ 10,6 μm za f ≈ 63 mm; u f = 100 mm a vstupu ~mm očekáváme podobný řád (~10 µm) → na 3,45 µm/px to jsou jednotky pixelů.

---

## 8. Pravidla vzorkování *z* (s citacemi)

### 8.1 ISO 11146 rodina (1999 principy + veřejné restatements 11146-1)

Opakovaně uváděno (DataRay, Ophir, Thorlabs, **Kovalev 2022** Intro):

1. Vytvoř měřitelný pas fokusující optikou. 
2. Změř šířku v **≥ 10** rovinách *z* (minimum, ne optimum — více je lepší). 
3. **≥ 5** bodů v pásmu **|z-z₀| ≤ zᵣ** (kolem pasu, obě strany). 
4. **≥ 5** bodů v dalekém poli **|z-z₀| ≥ 2 zᵣ**. 
5. Šířka pro ISO M² = **druhé momenty (D4σ)**; fit hyperboly d²(z)=a+bz+cz². 
6. ISO 1999 §7.1: na **každé** poloze *z* zopakuj mapu intenzity **≥ 5×**.

Proč obě oblasti: body jen u pasu nechají divergenci volnou → M² často falešně → 1 (DataRay).

### 8.2 Langer 2013

- Caustika Ti:sapphire: ~**−1 až +1 mm**, řádově **~20** profilů.
- Gaussův řez → 1/e² w → fit w(z) → w₀, M².
- **Pozor (limity studie):** **nepoužívají D4σ / druhé momenty**; M² je z Gaussovy caustiky (vizuálně/fit), typicky **1 frame na z**. Pro ISO-inspired M² u nás bereme spíš Kovalev/ISO větev.
- **Mapování:** u nás kolem pasu hustý scan na škále ~±1–2 mm (u krátkého zᵣ); celkem klidně 15–25 bodů; raději ≥5 framů/z.

### 8.3 Bonnett 2021

- Vizuální pas; pak **±5 mm po 1 mm → 11 pozic**.
- Na každé: **10 framů**.
- w = 2σ z Gaussova fitu projekcí; wₓᵧ = √((wₓ² + wᵧ²)/2).
- Fit w(z) → w₀, z₀, zᵣ.
- **Kontrola (opraveno):** π w₀² / zᵣ = **M² · λ** (ne přímo λ). Pro téměř ideální svazek M² ≈ 1 → výsledek ≈ λ; jinak očekávej M²·λ. Bonnett reportoval obnovení λ bez explicitního M².
- **Pozor:** Bonnett **nepočítá M²** — jen w₀, zᵣ, θ. M² bereme z ISO/Kovalev větve (+ Langer jako motivace).
- **Mapování:** „11 bodů / 1 mm“ jako **hrubý** průzkum; u našeho kratšího zᵣ **zahušť near-waist** (0,1–0,2 mm).

### 8.4 Kovalev 2022 (ISO větev)

- Recept ISO: ≥10 řezů, ≥5 u pasu. 
- Oni reálně **143 řezů po 1 mm** (luxus motorického stoleku; f′ = 550 mm → dlouhé zᵣ). 
- Druhé momenty → efektivní poloměr **wₑff = √(2(σₓ² + σᵧ²))** (= 2σ pro kruhový Gauss; dříve chybně 2√(σₓ²+σᵧ²), o √2 větší) → hyperbola → M². 
- **Mapování:** my **neděláme 143 bodů**; děláme **ISO minimum + rezervu** (např. 12–20) na ručním PT1/M. TIE větev **neděláme**.

### 8.5 Odhad w₀, pixelů a zᵣ (náš f = 100 mm)

Očekávaný pas (tenká čočka, M² ≈ 1):
**w₀ ≈ λ f / (π w_in)**.
Při λ = 532 nm, f = 100 mm a předpokladu w_in ≈ 1,75 mm (polovina Ø 3,5 mm z datasheetu CPS ve vzdálenosti 50,8 mm — **ověř na štítku**):
w₀ ≈ 9,7 µm ≈ **2,8 px** (pixel 3,45 µm) → průměr **2w₀ ≈ 5–6 px**.
To sjednocuje dřívější „pas 5–6 px“ (= průměr 2w₀), ne poloměr w₀.

Rayleigh (M² ≈ 1): **zᵣ ≈ π w₀² / λ** ≈ 0,55–0,6 mm; 2 zᵣ ≈ 1,1–1,2 mm.
**PT1/M 25 mm bohatě stačí** na far-field; kritické je **jemné** krokování kolem pasu.

### 8.6 Doporučená praktická mřížka (po hrubém odhadu pasu)

1. **Hrubý scan:** např. 11 bodů po 1 mm přes střed zdvihu (Bonnett-styl) → hrubý fit → odhad z₀, zᵣ.
2. **Finální run:**
   - ≥5 bodů v [z₀ − zᵣ, z₀ + zᵣ] s krokem ~0,1–0,2 mm;
   - několik bodů mezi zᵣ a 2 zᵣ;
   - **Far field symetricky:** ≥5 bodů s |z − z₀| ≥ 2 zᵣ **před pasem** a ≥5 bodů **za pasem** (obě strany caustiky), pokud to zdvih a velikost spotu na čipu dovolí. ISO minimum je ≥5 far celkem; symetrie zlepší fit.
3. Celkem **≥ 10**, ideálně **15–20**.
4. **Backlash PT1/M:** každou polohu z najížděj **vždy ze stejného směru**. Při přejetí couvni ≥ 1 mm a znovu najedi správným směrem.

---

## 9. Akvizice na jedné poloze *z*

1. Nastav mikrometr (**jeden směr najíždění**, viz §8.6) → zapiš z [mm] (nejistota ~±10 µm).
2. Zkontroluj saturaci / clip.
3. Ulož **≥ 5** (lépe **10**, Bonnett) framů: `zXXXXXum_frameK.tif`.
4. **ND během celého z-scanu NEMĚŇ.** Skleněný ND posouvá fokus přibližně o Δz ≈ t(1 − 1/n) (t = tloušťka, n ≈ 1,5) — řádově srovnatelné s naším zᵣ (~0,5 mm). Když potřebuješ jinou intenzitu, měň **expoziční čas** (nebo gain), ne filtr.
5. Background: laser zakrytý, stejná expozice → `bg_expoXXXX.tif` (ideálně na začátku a na konci runu).

---

## 10. Background, ROI, clipování

| Požadavek | Zdroj | Praxe |
|-----------|-------|-------|
| Odečíst background mapu (paprsek blokován) | ISO 1999 §6.4 | Povinné před D4σ; vhodné i před Gaussem |
| **float64 před odečtem** | praxe / uint16 underflow | `img.astype(np.float64) - bg` — nikdy neodečítej v uint16 |
| Integrace ≥ ~99 % výkonu | ISO 1999 | ROI kolem centroidu |
| **Adaptivní ROI — POVINNÉ pro D4σ** | Ophir / ISO praxe | Nikdy neintegruj celý čip. ROI ≈ **3–4× průměr svazku** kolem centroidu; iteruj (odhad σ → nová ROI → nové momenty), dokud nekonverguje (~±6σ okno) |
| Clip &lt; ~1 % | ISO §6.2 | Kontrola největšího spotu |
| Nyquist / dost pixelů | DataRay ≥10× px; Ophir &gt;20 px | Náš **2w₀ ≈ 5–6 px** = **slabé** |

---

## 11. Analýza: Gauss (1/e²) vs D4σ (ISO)

### 11.1 Primární cesta SVK — Gauss (Langer, Bonnett)

1. Načti snímky jako **float64**, odečti background, zprůměruj framы (nebo fitni každý a zprůměruj w).
2. Projekce X/Y nebo 2D Gauss:
   g(x) = (a / (σ √(2π))) · exp(−(x−μ)² / (2σ²)) + b.
3. Poloměr 1/e²: **w = 2σ** (Bonnett).
4. Převod: w [µm] = w [px] × 3,45.
5. Fit caustiky:
   w(z) = w₀ √(1 + ((z−z₀)/zᵣ)²).
6. Divergence (half-angle): θ ≈ w₀ / zᵣ.
7. Kontrola: **π w₀² / zᵣ = M² · λ**. Při M² ≈ 1 je to ≈ λ (Bonnett „obnovil“ 532 nm); obecně to není čisté λ.

**Langer:** Gauss fit může dát sub-pixelovou precizi u TEM₀₀; **nedělá D4σ**, M² z Gaussovy caustiky, často 1 frame/z — inspirace workflow, ne ISO metrologie.
**Bonnett:** výborný návod na ND + multi-frame Gauss; **bez M²**.

### 11.2 Volitelná ISO cesta — D4σ + M² (vzorce ověřeny)

1. float64 − background; **adaptivní ROI** kolem centroidu (3–4× průměr, iterace) — **nikdy celý čip**.
2. Centroid (1. momenty), pak σₓ², σᵧ² (2. momenty) jen uvnitř ROI.
3. Šířky:
   - průměry D4σ: **dσₓ = 4σₓ**, **dσᵧ = 4σᵧ**;
   - efektivní poloměr: **wₑff = √(2(σₓ² + σᵧ²))** (= 2σ pro kruhový Gauss);
   - pro ideální TEM₀₀: dσ = 2w (1/e² průměr).
4. Fit hyperboly — **pozor na to, co fituješ (w vs d = 2w)**; faktor 4 v M²:

**Varianta A — fituješ poloměry:** w²(z) = a + b z + c z²

- w₀ = √(4ac − b²) / (2 √c)
- z₀ = −b / (2c)
- zᵣ = √(4ac − b²) / (2c)
- θ = √c   (half-angle)
- M² = (π / (2λ)) · √(4ac − b²)

**Varianta B — fituješ průměry D4σ:** d²(z) = a + b z + c z²

- d₀ = √(4ac − b²) / (2 √c)
- z₀ = −b / (2c)
- zᵣ = √(4ac − b²) / (2c)
- θ = √c / 2   (half-angle, protože d = 2w)
- M² = (π / (8λ)) · √(4ac − b²)

5. Simple astigmatic: X a Y zvlášť.
6. Do SVK: *„ISO 11146–inspired estimate; 2w₀ ≈ 5–6 px limits accuracy.“*

**Clip-level / D86 nepoužívej pro M².**

### 11.3 Co nepočítáme

- **TIE** (Kovalev) — mimo SVK.
- Knife-edge / LDR (Bonnett) — nemáme setup.

---

## 12. Co zapisovat do logu (kompletní seznam)

**Hlavička runu**
- datum, čas, operátor, místnost, teplota (orientačně) 
- laser: model (foto), λ, třída, napájení 
- čočka: f, typ (LA1050…), vzdálenost laser–čočka [mm], držák 
- kamera: CS165MU/M, S/N, pixel µm, ThorCam verze 
- ND: konkrétní OD 
- definice z=0, směr *z*, jednotky mikrometru 

**Na každém *z***
- z [mm], expo [µs], gain, počet framů, cesty k souborům 
- poznámka: saturace? clip? elipsa? 

**Po vyhodnocení**
- w₀,z₀,zᵣ,θ (± odhad) 
- případně M²ₓ, M²ᵧ + caveat pixelů 
- cesta ke grafu w(z) v `vyhodnoceni/`

---

## 13. Typické poruchy (failure modes)

| Symptom | Pravděpodobná příčina | Co udělat |
|---------|----------------------|-----------|
| Plochý vrchol profilu | Saturace | ↑ ND / ↓ expo |
| M² ≪ 1 nebo nestabilní | Clip křídel / moc agresivní background | Zkontroluj daleké pole; mírnější ROI |
| M² ≈ 1 i když svazek vypadá špatně | Málo far-field bodů | Doplň body za 2 zᵣ **na obou stranách** pasu |
| Obří M² | Offset, ambient, šum v křídlech | Background; tma kolem setupu (ISO §6.3) |
| Pas „skáče“ | Vůle stolu (backlash) | Vždy najíždět z jednoho směru; při přejetí ≥1 mm zpět |
| Silná elipsa | CPS520 / náklon | Reportuj wₓ,wᵧ zvlášť |
| Spot mimo čip ve far field | Špatné zarovnání / moc velká caustika | Přesuň střed; zkrať rozsah *z* ale zachovej ≥5 far bodů |

---

## 14. Mitigace malého pasu (~5–6 px)

1. **Přijmout limit** — hlavní výsledek = w(z), z₀, řád w₀; M² jen s disclaimerem. 
2. **Změnit vzdálenost laser–čočka** (mírně rozostřit vstup) → větší fokusovaný spot; **zapsat geometrii**. 
3. Delší f / zvětšovací relay — mimo minimální SVK. 
4. Více framů + Gauss fit (Langer sub-pixel) — pomůže 1/e², **neplně** nahradí 20 px pro D4σ.

---

## 15. ISO 1999 vs co dělají studie vs nárok SVK

| Téma | ISO 11146:1999 (sample) | Langer 2013 | Bonnett 2021 | Kovalev 2022 | **Náš SVK** |
|------|-------------------------|-------------|--------------|--------------|-------------|
| Šířka pro M² | 2. momenty | Gauss 1/e² (+ M² z caustiky) | Gauss 2σ, **bez M²** | ISO 2. momenty (+ TIE) | Primárně Gauss; M² volitelně D4σ |
| Počet *z* | praxe ≥10 (moderní restatements) | ~20 na ±1 mm | 11 × 1 mm | ISO min.; oni 143 | ≥10–20, ISO near/far |
| Opakování | ≥5 map / *z* | — | 10 framů | hustý scan | ≥5–10 framů |
| Background | ano, zdůrazněno | offset 16 u webcam | lineární nastavení | ano (ISO) | **povinné** |
| Certifikace | norma | lab paper | lab paper | lab paper vs ISO | **„ISO-inspired estimate“**, ne certifikát |
| 2021 update | Part 1/2 split, TR-3 background | — | — | cituje ISO 11146 | Ověřit v NTK při potřebě formální citace |

**Formulace do SVK (EN návrh):** 
*Beam widths were obtained primarily from Gaussian 1/e² fits. An optional beam-quality factor M² was estimated from a hyperbolic fit to second-moment diameters following the sampling philosophy of ISO 11146 (focused caustic; ≥10 planes with points near the waist and in the far field). Because the focused waist spanned only ~5–6 camera pixels, the M² value is reported as an indicative, ISO-inspired estimate rather than a standards-compliant certification.*

---

## 16. Pořadí práce (shrnutí „od A do Z“)

1. Bezpečnost + foto štítku + složka dat + log. 
2. Sestavení osy; ND na kameře; ThorCam. 
3. Zarovnání; kontrola clipu v dalekém poli. 
4. Najít pas; odhad px; případně mitigace. 
5. Hrubý *z*-scan → odhad zᵣ. 
6. Finální mřížka (ISO near/far) + ≥5–10 framů/bod + background. 
7. Offline Python: background → Gauss caustika → (volitelně) D4σ/M². 
8. Záloha; laser VYP; doplnit Results do fulltextu.

---

## 17. Odkazy na lokální zdroje

- Krátký checklist: `03_mereni/postup_experimentu_2A4.pdf` / `postup_experimentu.md` 
- ISO digesty: `02_svk/papers/iso11146/` 
- Langer / Bonnett / Kovalev: `02_svk/papers/*_digest.md` 
- Kostra práce: `02_svk/fulltext_draft.md`

---

*Dokument sestaven 6. 11. 2026 pro SVK „Construction and Application of a Low-Cost Laser Beam Profiler“ (Marek Jelínek). Není náhradou zakoupeného textu ISO 11146-1:2021.*
