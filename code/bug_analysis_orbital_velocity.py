"""
Analysis of the "6 vs 6000" question in nkt_stability_tool_original.py.

Finding: the wave orbital velocity calculation (Uwc1 / Uwc2) wraps an already
dimensionless sinh() argument (2*pi*h/L) in an extra np.radians() call. That
argument is not an angle in degrees, so the conversion is wrong and inflates
the computed orbital velocity by roughly 70x for typical nearshore conditions.

This is checked against one real data point from Hydroinput_sample.csv
(point_ID 37.919) using the combo-1 wave/current pair (WHS10, Tp10, CU100).
"""
import numpy as np

g = 9.81

# real input row: point_ID 37.919
FA, SR, SP = 35, 0.04, 0.3
WL = 18.1          # used as water depth h in the tool
WHS10, Tp10 = 3.86, 8.8


def wavelength(T, h):
    L = 5.0
    error = 1.0
    while error > 0.001:
        L_new = (g * T ** 2 / (2 * np.pi)) * np.tanh(2 * np.pi * h / L)
        error = abs((L_new - L) / L_new)
        L = L_new
    return L


Ls = wavelength(Tp10, WL)
arg = 2 * np.pi * WL / Ls
print(f"wavelength L = {Ls:.2f} m, kh = 2*pi*h/L = {arg:.4f}")

Uw_as_written = (np.pi * WHS10) / (Tp10 * np.sinh(np.radians(arg)))
Uw_standard = (np.pi * WHS10) / (Tp10 * np.sinh(arg))

print(f"Uw as written in the code (extra radians() wrap): {Uw_as_written:.2f} m/s  <- unphysical")
print(f"Uw per standard linear wave theory (no wrap):      {Uw_standard:.2f} m/s  <- realistic")
print(f"ratio: {Uw_as_written / Uw_standard:.1f}x")

print(
    "\nFix: remove np.radians() around the sinh() argument in both Uwc1 and "
    "Uwc2 (two occurrences, in the combo-1 and combo-2 blocks)."
)
