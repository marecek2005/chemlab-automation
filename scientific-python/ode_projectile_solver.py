import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


def projectile(m, phi, v, h, t_end, method, steps):

    # --- initial conditions ---
    g = 9.81
    phi = math.radians(phi)

    vx = v * math.cos(phi)
    vy = v * math.sin(phi)

    # --- ODE system ---
    def f(t, y):
        y_pos, y_vel = y
        return [y_vel, -g]

    # --- time grid ---
    t_eval = np.linspace(0, t_end, steps)

    # ======================================================
    # solve using scipy
    # ======================================================
    if method.lower() != "euler":

        sol = solve_ivp(
            f,
            (0, t_end),
            [h, vy],
            method=method,
            t_eval=t_eval
        )

        t = sol.t
        y = sol.y[0]
        v = sol.y[1]

    # ======================================================
    # Euler method
    # ======================================================
    else:
        dt = t_end / steps

        t = np.zeros(steps + 1)
        y = np.zeros(steps + 1)
        v = np.zeros(steps + 1)

        t[0] = 0.0
        y[0] = h
        v[0] = vy

        for i in range(steps):
            v[i + 1] = v[i] - g * dt        # velocity first
            y[i + 1] = y[i] + v[i + 1] * dt # then position
            t[i + 1] = t[i] + dt

    # ======================================================
    # energies
    # ======================================================
    x = vx * t
    Ek = 0.5 * m * (v**2 + vx**2)
    Ep = m * g * y
    E  = Ek + Ep

    # ======================================================
    # impact point
    # ======================================================
    impact_x = None
    for i in range(len(y) - 1):
        if y[i] * y[i + 1] < 0:
            impact_x = x[i]
            break

    if impact_x is not None:
        print(f"Impact at x ≈ {impact_x:.2f} m")

        # ======================================================
    # plots: separate, clean, logical
    # ======================================================
    fig, axes = plt.subplots(
        3, 1,
        figsize=(10, 9),
        sharex=True
    )

    # ------------------------------------------------------
    # 1) Trajectory
    # ------------------------------------------------------
    axes[0].plot(x, y, color="red", label="y(x)")
    axes[0].set_ylabel("Height y [m]")
    axes[0].legend()
    axes[0].grid(True, linestyle="--", alpha=0.4)

    # ------------------------------------------------------
    # 2) Vertical velocity
    # ------------------------------------------------------
    axes[1].plot(x, v, color="purple", label=r"$v_y(x)$")
    axes[1].set_ylabel(r"Velocity $v_y$ [m·s$^{-1}$]")
    axes[1].legend()
    axes[1].grid(True, linestyle="--", alpha=0.4)

    # ------------------------------------------------------
    # 3) Energies
    # ------------------------------------------------------
    axes[2].plot(x, Ek, label="Kinetic energy", alpha=0.8)
    axes[2].plot(x, Ep, label="Potential energy", alpha=0.8)
    axes[2].plot(x, E,  label="Total energy", linewidth=2)

    axes[2].set_xlabel("Horizontal distance x [m]")
    axes[2].set_ylabel("Energy [J]")
    axes[2].legend()
    axes[2].grid(True, linestyle="--", alpha=0.4)

    # ------------------------------------------------------
    # Impact marker (optional, but nice)
    # ------------------------------------------------------
    if impact_x is not None:
        for ax in axes:
            ax.axvline(impact_x, color="black", linestyle=":", alpha=0.6)

    fig.suptitle(f"Projectile motion ({method})", fontsize=14)
    plt.tight_layout()
    plt.show()

# ======================================================
# parameters
# ======================================================
m = 13
phi = 85
v = 100
h = 20
t_end = 23
steps = 2000

projectile(m, phi, v, h, t_end, "euler", steps)
