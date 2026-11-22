import pyvisa
import time
import csv

TARGET_SERIAL = "04681995" #seriové číslo konkrétního přístroje dmm6500
#změnit pro použití u jiného 

#funkce která najde zařízení
def pick_usb_resource(serial=TARGET_SERIAL):
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    #print(resources)
    
    usb_resources = [res for res in resources if res.startswith("USB") and res.endswith("::INSTR")]
    #print(usb_resources)
    if not usb_resources:
        raise RuntimeError("V systému nebylo nalezeno žádné USB VISA zařízení.")

    serial_matches = [res for res in usb_resources if serial in res]
    #print(serial_matches)
    return serial_matches[0]

def initialize_instr(instr_ID):
    # 1. Inicializace VISA Resource Manageru
    rm = pyvisa.ResourceManager()

    #print(f"\nPoužívám USB zařízení: {instr_ID}")
    return rm.open_resource(instr_ID)
    
def choose_measurement_type(inst,choice):
    
    # Formální nastavení timeoutu pro USB operace (v milisekundách)
    inst.timeout = 2000 
    
    # 4. Inicializace přístroje (TSP příkazy)
    # Metoda write() pošle příkaz, ale nečeká na odpověď přístroje
    inst.write("reset()")
    time.sleep(1) # Počkáme na dokončení vnitřního resetu přístroje

    if choice == 1:
        inst.write("dmm.measure.func = dmm.FUNC_DC_VOLTAGE")
        symbol = "mV"
        name = "Napětí"
    elif choice == 2:
        inst.write("dmm.measure.func = dmm.FUNC_DC_CURRENT")
        symbol = "A"
        name = "Proud"
    else:
        raise ValueError("Invalid input. Enter 1 (voltage) or 2 (current).")

    
    print("\nZačínám měřit. Pro ukončení stiskni Ctrl+C")
    return symbol, name 

def start_measuring(inst, symbol, name, interval=1.0):
    # 5. Real-time smyčka
    start_time = time.time()
    next_run = start_time
    try:
        while True:
            now = time.time()
            wait = next_run - now
            if wait > 0:
                time.sleep(wait)
                continue

            voltage_str = inst.query("print(dmm.measure.read())")
            measurement_time = time.time()

            try:
                voltage = float(voltage_str.strip())
            except ValueError:
                print(f"Neočekávaná odpověď: {voltage_str}")
            else:
                elapsed_time = measurement_time - start_time
                csv_writer.writerow([elapsed_time, voltage])
                csv_file.flush()
                print(f"Čas: {elapsed_time:7.2f} s | {name}: {voltage*1e3:0.4f} {symbol}")

            next_run += interval
            if next_run <= measurement_time:
                next_run = measurement_time + interval
    except KeyboardInterrupt:
        print("\nMěření ukončeno uživatelem.")
    finally:
        inst.close()
        csv_file.close()

csv_file = open("measurements.csv", "w", newline="")
csv_writer = csv.writer(csv_file)

connected_instr = pick_usb_resource(serial=TARGET_SERIAL)
instr = initialize_instr(connected_instr)
symbol, name = choose_measurement_type(instr,1)
print(symbol,name)
start_measuring(instr, symbol, name)
