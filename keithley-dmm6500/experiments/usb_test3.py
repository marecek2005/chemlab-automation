import pyvisa
import time
import sys
import csv

csv_file = open("measurements.csv", "w", newline="")
csv_writer = csv.writer(csv_file)


TARGET_SERIAL = "04681995" #seriové číslo konkrétního přístroje dmm6500
#změnit pro použití u jiného 


#funkce která najde zařízení
def pick_usb_resource(resources, serial=TARGET_SERIAL):
    usb_resources = [res for res in resources if res.startswith("USB") and res.endswith("::INSTR")]
    if not usb_resources:
        raise RuntimeError("V systému nebylo nalezeno žádné USB VISA zařízení.")

    serial_matches = [res for res in usb_resources if f"::{serial}::" in res]
    return serial_matches[0] if serial_matches else usb_resources[0]

def initialize_instr():
    # 1. Inicializace VISA Resource Manageru
    
    # 2. Identifikace zařízení
    print("Dostupná zařízení v systému:")
    resources = rm.list_resources()
    for res in resources:
        print(f" - {res}")

    usb_resource_string = pick_usb_resource(resources)
    print(f"\nPoužívám USB zařízení: {usb_resource_string}")
    
    return usb_resource_string

try:
    rm = pyvisa.ResourceManager()
    # 3. Vytvoření spojení s přístrojem
    inst = rm.open_resource(initialize_instr())
    
    # Formální nastavení timeoutu pro USB operace (v milisekundách)
    inst.timeout = 2000 
    
    # 4. Inicializace přístroje (TSP příkazy)
    # Metoda write() pošle příkaz, ale nečeká na odpověď přístroje
    inst.write("reset()")
    time.sleep(1) # Počkáme na dokončení vnitřního resetu přístroje

    choice = sys.argv[1].strip() if len(sys.argv) > 1 else input("Enter 1 for voltage or 2 for current: ").strip()
    if choice == "1":
        inst.write("dmm.measure.func = dmm.FUNC_DC_VOLTAGE")
        symbol = "mV"
        name = "Napětí"
    elif choice == "2":
        inst.write("dmm.measure.func = dmm.FUNC_DC_CURRENT")
        symbol = "A"
        name = "Proud"
    else:
        raise ValueError("Invalid input. Enter 1 (voltage) or 2 (current).")

    
    print("\nZačínám měřit. Pro ukončení stiskni Ctrl+C")
    start_time = time.time()

    # 5. Real-time smyčka
    while True:
        # Intuitivně: Zeptáme se a rovnou dostaneme odpověď.
        # Formálně: Metoda query() kombinuje inst.write() a inst.read().
        # Odešle dotaz a zablokuje vlákno, dokud přístroj nepošle data zpět.
        voltage_str = inst.query("print(dmm.measure.read())")
        
        
        try:
            # Očištění o bílé znaky (\n, \r) a převod na desetinné číslo
            
            voltage = float(voltage_str.strip())
            elapsed_time = time.time() - start_time

            csv_writer.writerow([elapsed_time, voltage])
            csv_file.flush()
            print(f"Čas: {elapsed_time:7.2f} s | {name}: {voltage*1e3:0.4f} {symbol}")
            
        except ValueError:
            print(f"Neočekávaná odpověď: {voltage_str}")
            
        # Omezení frekvence dotazů (cca 10 Hz)
        time.sleep(5) 

except pyvisa.errors.VisaIOError as e:
    print(f"\nChyba komunikace VISA: {e}")
    print("Zkontroluj: 1. Je přístroj zapnutý a připojený přes USB?")
    print("           2. Zadal jsi správný usb_resource_string?")
except KeyboardInterrupt:
    print("\nSběr dat přerušen uživatelem.")
finally:
    # 6. Úklid a uvolnění prostředků
    if 'inst' in locals():
        inst.close()
    rm.close()
    csv_file.close()
