#!/usr/bin/env python3
# Interactive s-plane viewer for Re{e^{st}} using matplotlib.
# Click in the left plot to pick s = σ + jω; the right plot shows e^{σ t} cos(ω t).
# Keyboard: ↑/↓ t_max ×1.1/÷1.1, →/← samples ×1.1/÷1.1, r reset.
import numpy as np
import matplotlib.pyplot as plt

state = {"sigma":0.0,"omega":1.0,"t_max":10.0,"n_samples":2000,"xlim":(-3,3),"ylim":(-10,10)}
fig_s, ax_s = plt.subplots(figsize=(5,5))
ax_s.set_title("s-plane (click to choose s = σ + jω)")
ax_s.set_xlabel("σ (Real axis)"); ax_s.set_ylabel("ω (Imag axis)")
ax_s.set_xlim(*state["xlim"]); ax_s.set_ylim(*state["ylim"])
ax_s.axhline(0, lw=1); ax_s.axvline(0, lw=1); ax_s.set_aspect("equal", adjustable="box")
for x in np.linspace(state["xlim"][0], state["xlim"][1], 7): ax_s.plot([x,x], state["ylim"], lw=0.3, ls="--")
for y in np.linspace(state["ylim"][0], state["ylim"][1], 9): ax_s.plot(state["xlim"], [y,y], lw=0.3, ls="--")
(point_plot,) = ax_s.plot([state["sigma"]],[state["omega"]], "o", ms=8)
ann_s = ax_s.text(0.02,0.98,"", transform=ax_s.transAxes, ha="left", va="top")

fig_t, ax_t = plt.subplots(figsize=(7,4))
(line_time,) = ax_t.plot([], []); ax_t.axhline(0, lw=1); ax_t.set_xlabel("t"); ax_t.set_ylabel("Re{e^{st}}")

def compute(sigma, omega, tmax, ns):
    t = np.linspace(0, tmax, int(max(10, ns))); y = np.exp(sigma*t)*np.cos(omega*t); return t,y

def update_time():
    t,y = compute(state["sigma"], state["omega"], state["t_max"], state["n_samples"])
    line_time.set_data(t,y); ax_t.set_xlim(0,state["t_max"])
    m = max(1e-9, np.max(np.abs(y))); ax_t.set_ylim(-(m*1.05),(m*1.05))
    ax_t.set_title(f"Re{{ e^{{(σ+jω)t}} }} = e^({state['sigma']:.4g}·t) · cos({state['omega']:.4g}·t) "
                   f"(t_max={state['t_max']:.3g}, samples={int(state['n_samples'])})")
    fig_t.canvas.draw_idle()

def update_ann():
    ann_s.set_text(f"σ = {state['sigma']:.4g}\nω = {state['omega']:.4g}"); fig_s.canvas.draw_idle()

def on_click(ev):
    if ev.inaxes is not ax_s or ev.xdata is None or ev.ydata is None: return
    state["sigma"], state["omega"] = float(ev.xdata), float(ev.ydata)
    point_plot.set_data([state["sigma"]],[state["omega"]]); update_ann(); update_time()

def on_key(ev):
    if ev.key == "up": state["t_max"]*=1.1; update_time()
    elif ev.key=="down": state["t_max"]/=1.1; update_time()
    elif ev.key=="right": state["n_samples"]=int(state["n_samples"]*1.1); update_time()
    elif ev.key=="left": state["n_samples"]=max(10,int(state["n_samples"]/1.1)); update_time()
    elif ev.key=="r": state.update({"sigma":0.0,"omega":1.0,"t_max":10.0,"n_samples":2000}); point_plot.set_data([state["sigma"]],[state["omega"]]); update_ann(); update_time()

fig_s.canvas.mpl_connect("button_press_event", on_click)
fig_s.canvas.mpl_connect("key_press_event", on_key)
fig_t.canvas.mpl_connect("key_press_event", on_key)
update_ann(); update_time(); plt.show()
