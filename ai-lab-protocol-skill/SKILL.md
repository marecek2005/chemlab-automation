---
name: protokol
description: Vytváření a úpravy českých laboratorních protokolů z fyziky, fyzikální chemie, analytické chemie a přípravy nano a mikromateriálů z aktuálního návodu, dat a šablony. Použít při zadání /protokol nebo požadavku na laboratorní protokol, vyhodnocení měření či opravu existujícího protokolu.
---

## Protokol

## Přenositelné prostředí

- Považovat tento adresář za kořen skillu. Nepoužívat soubory z jiného účtu ani cesty původního autora.
- Přečíst [technický postup](references/technicky-postup.md) a [závislosti](references/zavislosti.md) před prací se soubory.
- Ověřit prostředí pomocí `python scripts/check_env.py`. Použít existující dostupné nástroje prostředí; jinak nastavit izolované prostředí podle přiloženého postupu.
- Původní vzor je fyzicky přiložen v `assets/VzorProt-Final.pdf`. Bez konkrétní šablony se řídit jeho formálními pravidly, nikoli jeho experimentem.
- Žádný konektor k Library, Drive ani žádný další placený skill není povinnou závislostí. Pro vstupy a výstupy použít dostupné souborové nástroje daného účtu. Úložiště obsluhovat podle pravidel hostitelského prostředí.

Vytvoř stručný, věcný a odevzdatelný protokol v češtině. Rozsah přizpůsob zadání a dostupným podkladům; nestanovuj univerzální počet stran.

Vytvoř stručný, věcný a odevzdatelný protokol v češtině. Rozsah určuj podle zadání; nepředepisuj počet stran ani dlouhou obecnou teorii.

### 1. Podklady a pravdivost

- Přečti aktuální zadání, potřebné části návodu, měření a poslední upravený dokument. Dodrž pořadí: pokyny uživatele → požadavky vyučujícího → aktuální návod → dodaný vzor → výchozí pravidla skillu.
- Vzor používej pro formu, ne pro převzetí jmen, hodnot, přístrojů či metod. Při volbě vzhledu přečti [vzor a styl](references/vzor-a-styl.md) .
- Interně přiřaď každému požadovanému výsledku zdroj dat a způsob výpočtu. Rozlišuj naměřené, předepsané, vypočtené a referenční údaje.
- Nevymýšlej měření, pozorování, podmínky, přesnost přístroje ani osobní údaje. Nečitelný nebo chybějící údaj nedoplňuj odhadem. Dokonči nezávislé části; na údaj nezbytný pro výsledek se konkrétně zeptej. Dopad sděl mimo protokol, podstatné vědecké omezení však v dokumentu nezamlčuj.
- Vypracuj pouze doložený a požadovaný rozsah. Chybějící výsledek nenahrazuj nulou; u pomlčky vysvětli, zda údaj chybí, nebo jej nelze určit.

### 2. Vzorky a provedené měření

- Propoj označení v návodu, datech a přístroji podle doloženého přiřazení. Nezaměň pozici přístroje za číslo vzorku; přeskočené pozice nezobecňuj.
- Odliš analyzované vzorky, standardy, slepý vzorek a referenci. Zachovej stejné názvy v textu, tabulkách i grafech; přečíslování nesmí přesunout hodnoty.
- Uveď relevantní složení, množství, koncentrace, objemy, ředění, přístroje a podmínky. Doloženou odchylku od návodu popiš jako skutečný postup.

### 3. Struktura a odborný text

Bez předepsané šablony použij toto pořadí; krátké související části můžeš sloučit:

1. Hlavička a název: předmět, úloha, autoři a datum podle podkladů.
2. Cíl: skutečně řešené úkoly podle zadání.
3. Postup: stručný, opakovatelný popis provedeného měření a přípravy vzorků.
4. Použité vztahy: relevantní rovnice, význam symbolů a potřebné parametry.
5. Výsledky: tabulky, grafy a reprezentativní výpočet každého odlišného typu.
6. Diskuse a závěr: konkrétní výsledky s jednotkami, odpovědi na cíle, podložené srovnání a omezení.

- Piš jasné, krátké věty s jednotnou terminologií. Zkratky vysvětli při prvním použití. Postup popisuj jednotně v minulém čase; nepřepisuj jej jako příkazy z návodu. Nezpracované úkoly nevydávej za splněné.
- Rozlišuj pozorování, výsledek výpočtu a interpretaci. Netvrď příčinu ani shodu v rámci nejistot bez opory. Externí hodnoty a tvrzení dolož ověřitelným zdrojem; podobu citací určuj podle zadání a pokynů uživatele.

### 4. Výpočty

- Přepočítej výsledky z původních dat. Ověř rozsahy tabulkových vzorců, přiřazení vzorků, převody, ředění a blank/baseline; korekci nezapočítej dvakrát. Pro konkrétní metodu načti pouze relevantní část [přehledu oborů](references/obory.md) .
- Kontroluj rozměrovou správnost. U empirických rovnic a regresních koeficientů uveď jednotky a podmínky platnosti; nezaměň veličinu za její číselnou hodnotu.
- Uveď vztah, vysvětlení symbolů a jedno dosazení s jednotkami. Další shodné výpočty shrň tabulkou. Zaokrouhluj až výsledky, podle skutečné přesnosti dat.
- Rozlišuj směrodatnou odchylku a jednotlivé druhy nejistot. Nepočítej statistiku z jediného měření; model nejistot i jejich zaokrouhlení určuj podle laboratoře.
- Regresi, vyřazení bodu, průchod počátkem či extrapolaci použij jen s důvodem. Referenční hodnoty ověř ve zdroji pro odpovídající podmínky.

### 5. Sazba, tabulky a grafy

- Zachovej ruční opravy a existující šablonu. Dílčí opravu omez na požadovaná místa a jejich důsledky. Používej styly, střídmé nadpisy a minimum tučného.
- Při sazbě načti [typografie](references/typografie.md) . Rozlišuj kurzívní veličiny od stojatých jednotek, funkcí, číslic, chemických značek a popisných indexů. V DOCX používej editovatelné rovnice OMML, pravé zlomky a indexy.
- Čísluj samostatné použité vztahy (1), (2), …; číslování nemusí mít každé dosazení ani krátký výraz v textu. Rovnice zapoj do věty včetně interpunkce.
- Umísti číslovaný název tabulky nad ni a popisek obrázku pod něj; grafy čísluj spolu s obrázky. V textu na ně odkazuj a vlož je poblíž příslušného výkladu.
- Uveď veličiny a jednotky v záhlaví i na osách; přednostně piš např. t / s nebo t (s) . V českém výstupu sjednoť desetinnou čárku. Vysvětli legendy, zkratky a případné škálování, aby tabulka či graf byly samostatně srozumitelné.
- Vlož grafy z doložených dat v kvalitě čitelné při finální velikosti. Použij vhodný původní graf nebo jej překresli; nevytvářej naměřené grafy generativně. Série odliš barvou i značkou/čárou, pomůže-li to černobílému tisku.
- Drž popisek s objektem, nadpis s navazujícím textem a malé tabulky vcelku. U dlouhých tabulek opakuj záhlaví a neděl řádky. Nezarovnávej mezerami, nevytvářej prázdné stránky a nekondenzuj řádky tak, aby se překrývaly indexy.

### 6. Kontrola a odevzdání

- Odstraň pracovní komentáře o Excelu, exportu, AI a technických problémech; zachovej odborný popis metody i omezení výsledků.
- Zkontroluj splnění úkolů, shodu text–tabulka–graf, jednotky, přesnost, odkazy, číslování, rovnice, indexy, české mezery a věcný závěr.
- Použij dostupné dovednosti pro dokumenty, PDF a tabulková data; samostatnou variantu popisuje [technický postup](references/technicky-postup.md). Finální DOCX vyrenderuj a prohlédni každou stránku; oprav ořez, kolize a nečitelné popisky. Nedostupnou vizuální kontrolu přiznej, netvrď, že proběhla.
- Výchozí výstup je DOCX; PDF přidej na přání nebo podle zadání. Ulož výsledek podle pravidel prostředí a zachovej identitu upravovaného souboru. Stručně sděl změny, odkaz na dokument a případný konkrétní nedořešený bod.

