import csv

def analyzuj_intervaly(soubor="measurements_dmm.csv", cilovy_interval=0.5):
    """
    Načte soubor CSV a vypočítá skutečné intervaly mezi měřeními.
    """
    casy = []
    
    try:
        with open(soubor, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # Přeskočíme hlavičku (Relativní čas, Napětí)
            
            for radek in reader:
                if radek:
                    # První sloupec je relativní čas (s)
                    casy.append(float(radek[0]))
                    
    except FileNotFoundError:
        print(f"Chyba: Soubor '{soubor}' nebyl nalezen. Nejdřív spusť měření.")
        return

    if len(casy) < 2:
        print("Nedostatek dat pro výpočet intervalů (je potřeba aspoň 2 body).")
        return

    # Vypočítáme rozdíly mezi sousedními body
    intervaly = []
    for i in range(1, len(casy)):
        rozdil = casy[i] - casy[i-1]
        intervaly.append(rozdil)

    # Statistika
    prumerny_interval = sum(intervaly) / len(intervaly)
    max_interval = max(intervaly)
    min_interval = min(intervaly)
    odchylka = prumerny_interval - cilovy_interval

    print(f"--- ANALÝZA INTERVALŮ ({soubor}) ---")
    print(f"Celkem načteno bodů:    {len(casy)}")
    print(f"Cílový interval:       {cilovy_interval:.6f} s")
    print(f"----------------------------------------")
    print(f"Průměrný interval:      {prumerny_interval:.6f} s")
    print(f"Odchylka od cíle:       {odchylka:+.6f} s")
    print(f"Relativní chyba:        {(odchylka / cilovy_interval) * 100:.4f} %")
    print(f"----------------------------------------")
    print(f"Nejkratší mezera:       {min_interval:.6f} s")
    print(f"Nejdelší mezera:        {max_interval:.6f} s")
    print(f"Rozptyl (max-min):      {max_interval - min_interval:.6f} s")

if __name__ == "__main__":
    # Zde můžeš změnit cílový interval podle toho, co jsi nastavil v usb_test_dmm.py
    analyzuj_intervaly("measurements_dmm.csv", cilovy_interval=0.5)
