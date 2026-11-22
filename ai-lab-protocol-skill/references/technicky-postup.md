# Samostatný technický postup

## Čtení podkladů

1. Zjistit dostupný Python a nástroje hostitelského prostředí. Spustit `scripts/check_env.py`, případně nastavit přiložené knihovny podle `references/zavislosti.md`.
2. PDF číst přes `pypdf.PdfReader`; při významu rozložení vykreslit stránky přes `scripts/render_docx.py vstup.pdf --output-dir kontrola`. Ke kontrole grafů, popisků a ručních zápisů použít obrazové čtení asistenta.
3. XLSX číst přes `scripts/read_xlsx.py vstup.xlsx`, případně doplnit `--sheet NAZEV --range A1:H40`. Skript vrací původní vzorce i uložené výsledky. Ty nepovažovat za důkaz správné recalculace; přepočítat důležité výsledky nezávisle. Výpočty chybějící ve zdroji nevymýšlet.
4. DOCX číst přes `python-docx` nebo OOXML. Při úpravě zachovat aktuální uživatelovy změny; nevygenerovat dokument znovu ze starší verze.
5. Data z CSV/TSV číst přes standardní Python `csv`; rozlišit desetinný a sloupcový oddělovač. Statistiku provést přes `statistics` nebo `numpy` dodávané s Matplotlib.

## Tvorba dokumentu

- Použít `python-docx`. Pomocné funkce z `scripts/docx_helpers.py` nastavují A4 a střídmý vzhled a vytvářejí editovatelné rovnice OMML.
- Při konkrétní šabloně její vzhled upřednostnit před výchozími funkcemi. Přiložený fyzikální vzor nepovažovat za univerzální zadání experimentu.
- Dolní a horní indexy ve větách a tabulkách nastavit přes `run.font.subscript` a `run.font.superscript`; chemické značky a jednotky ponechat stojaté.
- Strukturovanou rovnici psát jako OMML. Při sazbě dodržet `references/typografie.md`. Ve vlastních helper funkcích použít `math_run(text, upright=True)` pro stojaté funkce, číslice, operátory a popisné části; `subscript(base, index, index_upright=False)` pouze pro index představující proměnnou. Pro mocninu poměru vložit poměr do závorek a umocnit celou skupinu, ne samotný čitatel. U odmocniny použít `m:rad` s celým pododmocninovým výrazem.
- Definovat všechny symboly a jednotky; dosazení provést na plné přesnosti a až konečný výsledek zaokrouhlit.
- Grafy vytvářet Matplotlib z původních hodnot, s jednotkami, popisky a rozlišením více sérií. Exportovat PNG v tiskové kvalitě a vložit jej do dokumentu. Nevytvářet fiktivní chromatogram ze seznamu poloh a ploch píků.
- Tabulky číslovat nad tabulkou, obrázky pod obrázkem; grafy mají společnou řadu s obrázky. Zabránit rozdělení jednotlivého řádku tabulky mezi stránky.

## Ověření

1. Vytvořit interní mapu požadovaných výstupů a podkladů. Zkontrolovat každou položku zadání, jednotky, vzorky, čísla textu/tabulek/grafů a vazbu závěru na výsledky.
2. Ověřit, že balíček DOCX je čitelný ZIP s validním OOXML. Zachování rovnic a indexů ověřit také ve výsledném zobrazení.
3. Spustit `python scripts/render_docx.py vystup.docx --output-dir kontrola`.
4. Pokud LibreOffice chybí, exportovat stejnou finální verzi ve Wordu/LibreOffice do PDF a spustit stejný skript nad tímto PDF. Nezaměnit náhled starší verze za kontrolu aktuální verze.
5. Prohlédnout **každou** PNG stránku. Opravit překryvy, ořezané texty, chybné matematické zápisy a rozdělené titulky. Po změně render zopakovat. Pokud se žádná vizuální kontrola nepodařila, pravdivě to sdělit mimo protokol.
6. Vrátit požadovaný finální soubor, nikoliv pracovní obrázky nebo chybové záznamy. Výchozí výstup je DOCX; PDF pouze na přání či podle zadání.

## Rozsah přenosu

Nejsou vyžadovány konkrétní MCP názvy, soukromé identifikátory souborů, historie chatu ani další účet autora. Ověřování zdrojů a ukládání výsledků provádět dostupnými nástroji cílového prostředí. Použití slova `/protokol` v běžném chatu samo o sobě neinstaluje rozšíření; asistent musí mít přístup k tomuto SKILL.md a jeho souborům.
