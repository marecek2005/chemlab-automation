import pyvisa
import time
import csv
from pathlib import Path

TARGET_SERIAL = "04681995" # sériové číslo konkrétního přístroje DMM6500

def pick_usb_resource(serial=TARGET_SERIAL):
    # Pro ladění vypíšeme verzi pyvisa
    print(f"Ladicí info: PyVISA verze: {pyvisa.__version__}")
    
    backends = ['', '@py']
    all_resources = []
    
    for backend in backends:
        try:
            rm = pyvisa.ResourceManager(backend)
            res = rm.list_resources()
            for r in res:
                if r not in all_resources:
                    all_resources.append(r)
        except Exception:
            continue

    # Vyčistíme názvy zařízení od nulových znaků a mezer pro snadnější porovnání
    clean_resources = [r.replace('\x00', '').strip() for r in all_resources]
    
    usb_resources = [r for r in clean_resources if "USB" in r.upper()]
    
    if not usb_resources:
        print(f"Nalezená zařízení: {all_resources}")
        raise RuntimeError("V systému nebylo nalezeno žádné USB VISA zařízení.")
    
    # Hledáme shodu se sériovým číslem v "čistých" názvech
    for i, res_name in enumerate(clean_resources):
        if "USB" in res_name.upper() and serial in res_name:
            print(f"Úspěch! Používám zařízení: {all_resources[i]}")
            return all_resources[i]

    # Pokud neshoda, ale je tam jen jedno USB zařízení, zkusíme ho
    if len(usb_resources) == 1:
        # Najdeme původní (nevyčištěný) název
        idx = clean_resources.index(usb_resources[0])
        print(f"Sériové číslo nesedí úplně přesně, ale zkouším jediné nalezené USB: {all_resources[idx]}")
        return all_resources[idx]
        
    raise RuntimeError(f"Sériové číslo {serial} nenalezeno v {usb_resources}")

def initialize_instr(instr_ID):
    try:
        rm = pyvisa.ResourceManager('@py')
    except Exception:
        rm = pyvisa.ResourceManager()
    return rm.open_resource(instr_ID)

def setup_measurement(inst, interval=0.5):
    inst.timeout = 5000
    inst.write("reset()")
    time.sleep(1)
    
    # Nastavení měření
    inst.write("dmm.measure.func = dmm.FUNC_DC_VOLTAGE")
    # Vymazání interní paměti (bufferu), kam se budou ukládat data
    inst.write("defbuffer1.clear()")
    # Maximální počet naměřitelných dat v bufferu
    inst.write("defbuffer1.capacity = 100000") 
    
    # Hlavní příkaz nastaví 100000 měření po intervalu (DMM6500 používá .load('SimpleLoop', ...))
    inst.write(f"trigger.model.load('SimpleLoop', 100000, {interval})")
    
    #spuštění loopu
    inst.write("trigger.model.initiate()")
    print(f"\nZačínám měřit (HW interval {interval}s). Pro ukončení stiskni Ctrl+C")

def start_measuring(inst):
    csv_file = open("measurements_dmm.csv", "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Relativní čas (s)", "Napětí (V)"])

    last_index = 0
    try:
        while True:
            # Zjistíme, kolik bodů je aktuálně v bufferu
            current_n = int(inst.query("print(defbuffer1.n)").strip())
            
            #načte všechny nové body může být víc než 1
            if current_n > last_index:
                
                for i in range(last_index + 1, current_n + 1):
                    #vratí naměřenou hodnotu a čas
                    val = inst.query(f"print(defbuffer1[{i}])").strip()
                    t_rel = inst.query(f"print(defbuffer1.relativetimestamps[{i}])").strip()
                    
                    voltage = float(val)
                    elapsed = float(t_rel)
                    
                    csv_writer.writerow([elapsed, voltage])
                    print(f"Index: {i:5} | DMM Čas: {elapsed:7.3f} s | Napětí: {voltage:0.6f} V")
                
                csv_file.flush()
                last_index = current_n
            
            time.sleep(0.1) # Rychlé dotazování na stav bufferu
            
    except KeyboardInterrupt:
        print("\nMěření zastaveno. Ukončuji trigger model...")
        #pokud zmáčknu ctrl + c tak se zastaví měření i na přístroji
        inst.write("trigger.model.abort()")
    finally:
        inst.close()
        csv_file.close()

connected_instr = pick_usb_resource(serial=TARGET_SERIAL)
instr = initialize_instr(connected_instr)

#pozor už začíní měřit
setup_measurement(instr)
start_measuring(instr)

#poznámky pro mě:
# .strip() odstranění bílých znaků \n 
# flush() ukládání dat automaticky ne čekání na konec kodu
