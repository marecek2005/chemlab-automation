# Závislosti a spuštění

## Co je přibaleno

- Všechna pravidla, oborové reference, původní PDF vzor, tři PDF podklady typografie a odborného psaní a vlastní pomocné skripty.
- Python knihovny včetně jejich tranzitivních závislostí jako instalační wheels pro **CPython 3.11** na Linux x86_64, macOS arm64 a Windows x86_64. Wheels nejsou univerzální binární soubory; vybrat adresář odpovídající systému.
- `requirements.txt` určuje verze přímých závislostí. `requirements.lock.txt` určuje také verze tranzitivních závislostí. Licenční informace knihoven jsou zachovány uvnitř jejich wheels.

## Co poskytuje cílové prostředí

- Asistenta/LLM schopného číst instrukce skillu a používat souborové a spouštěcí nástroje. Samotný ZIP není autonomní aplikace.
- Python 3.11 pro offline instalaci. Python není přibalen jako instalační obraz operačního systému.
- Pro automatický převod DOCX do PDF nativní LibreOffice; alternativou je převod ve Wordu a vykreslení hotového PDF přiloženým skriptem. LibreOffice ani Word nejsou obsaženy v ZIPu.
- Pro OCR, pokud vstup nelze přečíst, použít dostupné vidění asistenta. OCR knihovna není nutná pro běžné čitelné podklady.

## Instalace Python knihoven bez sítě

Z kořene adresáře `protokol` spustit:

```sh
python3.11 scripts/setup.py
```

Ve Windows použít `py -3.11 scripts/setup.py`. Skript vytvoří `.venv` a nainstaluje všechny Python závislosti z přiložených wheels přes `--no-index`. Nepřenáší přihlašovací údaje a nevytváří sdílení.

Pak používat `.venv/bin/python` na Linux/macOS nebo `.venv/Scripts/python.exe` na Windows. Pokud hostitelské prostředí už knihovny poskytuje, vlastní venv není nutná; nejprve spustit kontrolu prostředí.

Pro jinou verzi Pythonu či architekturu není přibalen offline wheelhouse. Explicitní varianta `python scripts/setup.py --online` stáhne stejné požadované verze z PyPI pro dané prostředí; dostupnost binárních balíčků pro takové prostředí nebyla tímto exportem ověřena.

## Instalace převodníku DOCX do PDF

- Linux s Debian/Ubuntu a oprávněním instalovat balíčky: `apt-get update` a `apt-get install libreoffice-writer`.
- macOS s Homebrew: `brew install --cask libreoffice`.
- Windows: použít oficiální instalátor LibreOffice, případně `winget install --id TheDocumentFoundation.LibreOffice --exact`.
- Bez instalačních oprávnění použít existující Word/LibreOffice pro export PDF. Nevydávat strukturální kontrolu DOCX za vizuální kontrolu.

Instalace nativního programu může vyžadovat síť a oprávnění správce. Není přenosná mezi účty nebo operačními systémy jako pouhá konfigurace skillu.

## Ověření

```sh
.venv/bin/python scripts/check_env.py
.venv/bin/python scripts/check_env.py --require-render
```

Druhý příkaz požaduje i nativní LibreOffice. Jeho absence nebrání čtení dat ani vytvoření DOCX; brání pouze tomuto konkrétnímu automatickému převodu.

## Licenční rozsah

V balíčku nejsou kopie proprietárních systémových skillů Documents, PDF ani Spreadsheets. Jejich funkční návaznosti nahrazují zde přiložené vlastní pracovní postupy a skripty. Původní PDF vzor dodal uživatel a je určen jako reference pro použití tohoto skillu. Při dalším šíření zachovat práva autora PDF a licenční soubory knihoven. PyMuPDF je distribuován se svými licenčními podmínkami v přiloženém wheelu; jeho zahrnutí neposkytuje komerční licenci ani nemění podmínky původního projektu.
