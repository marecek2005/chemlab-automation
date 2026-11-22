# Ověření exportu

- Na macOS arm64 s čistým CPython 3.11.15 byla úspěšně provedena skutečná instalace všech 19 Python balíčků pouze z přiložených wheels, bez PyPI. Instalační skript používá přibalený pip a na Unixu symlinkovaný venv; nevyžaduje úspěšné `ensurepip`.
- Pro Linux x86_64 a Windows x86_64 byl úspěšně proveden offline resolver instalace pro CPython 3.11 nad příslušnými wheels. Běh na těchto dvou operačních systémech nebyl v tomto prostředí proveden.
- Všechny tři platformy mají shodné uzamčené verze 19 balíčků. Linux wheelhouse je určen pro glibc systémy kompatibilní s manylinux 2.28/2014; nezahrnuje Alpine/musl ani ARM Linux. macOS wheelhouse je určen pro Apple Silicon a macOS 11 nebo novější, nikoliv Intel Mac.
- Pomocný skript úspěšně načetl buňky XLSX. Funkce pro dokument vytvořily validní DOCX s editovatelnou rovnicí a umocněním celého poměru v závorkách.
- Přiložený PDF vzor byl načten a vykreslen do všech devíti PNG stran novým vlastním renderovacím skriptem. Převod DOCX přes nativní LibreOffice nebyl v této relaci zkoušen; hostitelská dovednost Documents jej zde nepovoluje a bundled převodník nebyl dostupný.
- Nezávislé použití pravidel na třech měřeních vytvořilo český DOCX se správným průměrem, výběrovou směrodatnou odchylkou a RSD. Vizuální kontrola tohoto interního DOCX neproběhla kvůli dostupnosti povoleného převodníku; strukturální a výpočtové kontroly prošly.
- Manifest kontroluje SHA-256 přiložených souborů. Konečný archiv byl ověřen jako čitelný ZIP bez `.git`, `.venv`, cache a soukromých identifikátorů účtu v pracovních pravidlech.

Tyto kontroly ověřují přenositelnost souborů a Python závislostí v popsaném rozsahu. Neprokazují automatickou instalaci skillu do UI každé varianty ChatGPT ani nativní převod DOCX na každém operačním systému.
