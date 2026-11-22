import pyvisa
import time
import csv

TARGET_SERIAL = "04681995" # sériové číslo konkrétního přístroje DMM6500

def pick_usb_resource(serial=TARGET_SERIAL):
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    usb_resources = [res for res in resources if res.startswith("USB") and res.endswith("::INSTR")]
    if not usb_resources:
        raise RuntimeError("V systému nebylo nalezeno žádné USB VISA zařízení.")
    serial_matches = [res for res in usb_resources if serial in res]
    return serial_matches[0]

def initialize_instr(instr_ID):
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
    
    # Nastavení přesného hardwarového časovače (Timer)
    inst.write("trigger.timer[1].reset()")
    inst.write(f"trigger.timer[1].delay = {interval}")
    # count = 0 znamená, že časovač bude tikat do nekonečna (dokud ho nevypneme)
    inst.write("trigger.timer[1].count = 0")
    # Časovač se "natáhne" signálem NOTIFY1
    inst.write("trigger.timer[1].start.stimulus = trigger.EVENT_NOTIFY1")
    # Zapnutí časovače (u DMM6500 je to 'enable')
    inst.write("trigger.timer[1].enable = trigger.ON")

    # Ruční sestavení trigger modelu pro DMM6500
    inst.write("trigger.model.setblock(1, trigger.BLOCK_BUFFER_CLEAR, defbuffer1)")
    # Blok 2 vyšle signál NOTIFY1, který odstartuje časovač nastavený výše
    inst.write("trigger.model.setblock(2, trigger.BLOCK_NOTIFY, trigger.EVENT_NOTIFY1)")
    # Blok 3 čeká na první (a každé další) tiknutí časovače
    inst.write("trigger.model.setblock(3, trigger.BLOCK_WAIT, trigger.EVENT_TIMER1)")
    # Blok 4 provede měření
    inst.write("trigger.model.setblock(4, trigger.BLOCK_MEASURE, defbuffer1)")
    # Blok 5 se vrátí na čekání (blok 3), dokud neudělá 100 000 měření
    inst.write("trigger.model.setblock(5, trigger.BLOCK_BRANCH_COUNTER, 100000, 3)")
    
    # Spuštění měřicího cyklu (trigger modelu)
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
            
            # Načte všechny nové body (může být víc než jeden)
            if current_n > last_index:
                
                for i in range(last_index + 1, current_n + 1):
                    # Vrátí naměřenou hodnotu a čas z bufferu
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
        # Pokud dojde k přerušení, zastavíme měření i na přístroji
        inst.write("trigger.model.abort()")
    finally:
        inst.close()
        csv_file.close()

connected_instr = pick_usb_resource(serial=TARGET_SERIAL)
instr = initialize_instr(connected_instr)

# Zahájení nastavení a měření
setup_measurement(instr)
start_measuring(instr)

# Poznámky:
# .strip() odstraní bílé znaky jako \n
# flush() zajistí okamžité uložení dat do souboru bez čekání na konec skriptu
