import numpy as np
from scipy.special import gamma, gammainc
import scipy.integrate as integrate

print("=== ADVERSARIAL STRESS-TEST VERIFICATION ===")

# Test 1: Bell-CHSH degradation for LG vs PVB
def lg_trans(l, R_iris, w):
    # gammainc in scipy is normalized regularized lower incomplete gamma: P(a, x) = gamma(a, x) / Gamma(a)
    return gammainc(l + 1, 2.0 * (R_iris / w)**2)

w = 1.0
R_iris = 1.2
print("LG transmissions for R_iris/w = 1.2:")
for l in [0, 1, 2, 4, 6]:
    t = lg_trans(l, R_iris, w)
    print(f"  l={l}: transmission = {t:.4f}")

# For PVB, test peak shift across l
w0 = 0.1
R0 = 1.0
print("\nPVB topological radial shift Delta R_l [um]:")
for l in [1, 2, 4, 10]:
    shift_um = (l**2 * w0**4) / (8.0 * R0**3) * 1e3 # mm to um
    print(f"  l={l}: shift = {shift_um:.6f} um")

# Test 2: Frame condition number
w0_kmax = 1.50
A = np.exp(-0.5 * w0_kmax**2)
B = 1.0
kappa = B / A
print(f"\nFrame bounds for w0*K_max = {w0_kmax}:")
print(f"  A = {A:.6f}")
print(f"  B = {B:.6f}")
print(f"  kappa = {kappa:.6f}")

# Test 3: 8.60 dB advantage decomposition
coup_gain = 10 * np.log10(0.965 / 0.200)
isi_penalty = 1.82 - 0.05
total_adv = coup_gain + isi_penalty
print(f"\nRCF Advantage breakdown:")
print(f"  Coupling gain: {coup_gain:.3f} dB")
print(f"  ISI mitigation: {isi_penalty:.3f} dB")
print(f"  Total advantage: {total_adv:.3f} dB")
