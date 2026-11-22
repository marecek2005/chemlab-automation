# Python prostředí pro měření laserového svazku

## Cíl projektu

Cílem projektu je postupně vytvořit jednoduché a přehledné prostředí v Pythonu pro práci s laboratorním uspořádáním a vyhodnocování vlastností laserového svazku.

Základní představa měření je následující:

1. Laser vytváří svazek.
2. Do dráhy svazku je vložena čočka.
3. Kamera je umístěna na posuvném stolku a zaznamenává profil svazku v různých polohách podél jeho šíření.
4. Python program pomáhá získávat snímky, přiřazovat jim polohu kamery a vyhodnocovat naměřená data.

Mezi předběžně zamýšlené výsledky patří profil intenzity svazku, jeho porovnání s Gaussovým rozdělením, velikost a poloha pasu svazku a Rayleighova délka. Přesný seznam veličin, jejich definice a způsob výpočtu upřesníme později. Zmíněná „vzdálenost v ústí laseru“ zatím není jednoznačně definována a bude potřeba si vyjasnit, co se tím myslí.

Zatím není rozhodnuto, zda se bude stolek posouvat ručně, nebo jej bude řídit program. Stejně tak zatím není součástí zadání přímé ovládání samotného laseru. Název „ovládání setupu“ zde znamená především práci s kamerou, měřením a daty; další zařízení přidáme podle konkrétního zadání.

## Kde se program vyvíjí a kde poběží

- **Mac:** hlavní místo pro psaní kódu, přípravu souborů a vysvětlování jednotlivých kroků.
- **Windows počítač v laboratoři:** místo pro připojení skutečného hardwaru a ověření komunikace se zařízeními.

V současném pracovním uspořádání nejsou na Macu k dispozici potřebné USB ovladače pro používaný hardware. Proto zde nelze ověřit celé měření se skutečnou kamerou. Dostupnost a požadavky konkrétního SDK a ovladačů upřesníme podle vybavení laboratorního počítače.

Zdrojové soubory se budou uchovávat a upravovat zde a následně přenášet na laboratorní Windows počítač. Způsob přenosu zatím není určen.

Části, které hardware nepotřebují, lze podle dostupných dat a knihoven ověřovat i na Macu, například výpočty nebo zpracování uložených snímků. Úspěšné spuštění takové části ale neznamená, že je ověřena také komunikace s kamerou ve Windows.

## Filozofie kódu

Autor projektu je začátečník v Pythonu. Hlavním požadavkem je, aby kódu rozuměl, dokázal jej upravovat a postupně se na něm učil.

1. **Srozumitelnost má přednost před stručností.** Delší a snadno pochopitelný zápis je lepší než krátký, ale obtížně čitelný trik.
2. **Používáme především základy Pythonu.** Jednoduché proměnné, podmínky, cykly `for`, seznamy a malé funkce podle potřeby.
3. **Složitější prostředky přidáváme jen tehdy, když jsou skutečně potřeba.** Pokud je vyžaduje například SDK kamery, vysvětlíme jejich význam a použití.
4. **Názvy mají říkat, co daná věc znamená.** U fyzikálních veličin uvádíme také jednotky v názvu proměnné nebo v jasném komentáři.
5. **Komentáře pomáhají porozumět postupu.** Vysvětlují zejména účel kroku, nové pojmy, jednotky a méně zřejmá místa. Nemusí opisovat každý jednoduchý řádek.
6. **Přidáváme pouze domluvené funkce.** Nevytváříme předem rozsáhlý framework, další režimy, simulátor ani grafické rozhraní bez konkrétní potřeby a zadání.
7. **Postupujeme po malých krocích.** Každá změna má mít jasný účel a má být možné vysvětlit, co dělá a jak ji ověřit.

## Rozdělení do souborů

Nechceme jeden dlouhý skript s tisícem řádků. Kód budeme rozdělovat do menších, smysluplně pojmenovaných souborů podle toho, co dělají.

Orientační rozsah jednoho souboru je přibližně **100 až 200 řádků**. Není to pevný limit ani cílová délka: krátký úkol může mít jen několik desítek řádků. Soubor rozdělíme tehdy, když to zlepší orientaci, ne pouze kvůli počtu řádků.

Postupně mohou podle potřeby vzniknout například:

- `hlavni.py` – spuštění a propojení jednotlivých kroků měření;
- `kamera.py` – připojení kamery a získávání snímků;
- `ukladani.py` – ukládání snímků a údajů o měření;
- `vyhodnoceni.py` – výpočty z naměřených dat;
- `grafy.py` – zobrazení výsledků.

Toto je pouze příklad budoucího členění, nikoli seznam souborů, které je nutné hned vytvořit. Soubory budeme přidávat až s konkrétní funkcí. Pro jejich propojení použijeme jednoduché importy a volání funkcí.

Komunikaci s hardwarem budeme podle potřeby držet odděleně od výpočtů. To usnadní orientaci i ověřování výpočtů na Macu bez připojené kamery.

## Jak budeme spolupracovat

Úlohou asistenta je pomáhat s programováním, hledáním chyb a pochopením kódu. Nemá pouze dodat hotové řešení, kterému autor nebude rozumět.

Při jednotlivých úkolech budeme:

1. Ujasňovat, jakou konkrétní věc má nový kód dělat.
2. Vytvářet nejjednodušší srozumitelné řešení odpovídající zadání.
3. Vysvětlovat nové konstrukce, důležité změny a způsob spuštění.
4. Uvádět, co bylo skutečně ověřeno na Macu a co je ještě potřeba vyzkoušet na Windows s hardwarem.
5. Po laboratorním ověření upravovat kód podle skutečného chování zařízení a naměřených dat.

Při přenosu mezi počítači budeme přednostně používat cesty odvozené od složky projektu. Pokud bude nutná cesta závislá na konkrétním Windows počítači, například k SDK, jasně ji označíme a vysvětlíme, kde ji změnit. S přidáváním knihoven budeme průběžně zapisovat, co je potřeba nainstalovat a jak program spustit.

## Co ještě upřesnit

Tyto otázky nebrání založení projektu. Budeme je řešit až při práci na příslušné části:

- Přesný model kamery, verze SDK a ovladačů a verze Pythonu na laboratorním Windows počítači.
- Zda bude posun kamery ruční, nebo řízený programem; odkud se bude získávat její poloha a vůči jakému počátku.
- První konkrétní úkol programu, například připojení kamery a uložení jednoho snímku.
- Zda má být první verze ovládaná jednoduchým skriptem, nebo později potřebujeme také grafické rozhraní.
- Přesné měřené veličiny, jejich definice a jednotky, včetně toho, jak budeme určovat šířku svazku.
- Parametry potřebné pro vyhodnocení, například vlnová délka laseru a převod mezi pixely snímku a skutečnými rozměry.
- Jaká data se mají ukládat spolu se snímkem, například poloha kamery, expozice a poznámka k měření.

## Současný stav

Projekt je ve fázi vymezení cíle a pravidel práce. Tato složka zatím obsahuje pouze tento dokument. Žádný měřicí program ani komunikace s hardwarem zatím nebyly vytvořeny nebo ověřeny.

README budeme průběžně aktualizovat tak, aby odpovídalo skutečnému stavu projektu a nově upřesněným požadavkům.
