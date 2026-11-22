import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
import os
from pathlib import Path

# Cesta k souboru ve stejném adresáři jako tento skript
CSV_FILE = Path(__file__).parent / "measurements_dmm.csv"


def read_csv():
    #Read all rows from the CSV file. Returns two lists: times, values.
    times = []
    values = []
    if not os.path.exists(CSV_FILE):
        return times, values
    with open(CSV_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 2:
                try:
                    times.append(float(row[0]))
                    values.append(float(row[1]))
                except ValueError:
                    pass
    return times, values


def update(frame):
    times, values = read_csv()
    if not times:
        return (line,)

    line.set_data(times, values)

    # auto-scale axes
    ax.set_xlim(0, times[-1] + 1)
    
    vmin, vmax = min(values), max(values)
    margin = max(abs(vmax) * 0.05, 1e-9)

    ax.set_ylim(vmin - margin, vmax + margin)

    return (line,)


# set up the plot
fig, ax = plt.subplots()
ax.set_xlabel("Čas [s]")
ax.set_ylabel("Hodnota")
ax.set_title("Real-time měření")
(line,) = ax.plot([], [])

# refresh every 500ms
ani = animation.FuncAnimation(fig, update, interval=500)

plt.show()