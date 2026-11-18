# Referee 2 Report: Exhaustive Technical, Mathematical, Editorial, and Bibliographic Audit

**Manuscript Evaluated:** `p3_3/main.tex` — *"Overcompleteness and Continuous Frame Properties of Physical Perfect Vortex Beams"*  
**Journal Target:** *Physical Review A* (APS)  
**Referee Role:** Referee 2 (Exhaustive Audit of Theoretical Approach, Structure, Scientific Writing, References, Citations, and Calculations)  
**Executive Recommendation:** **Major Revision**

---

## Scope of Audit

A complete, line-by-line audit of `c:\Users\sayal\OneDrive\Desktop\Papers\p3_3\main.tex` (596 lines, 39,419 bytes) was conducted across all 41 numbered equations in the main text (`Eq. (1)`–`Eq. (41)`), both appendices (`App. A`: `Eqs. (A1)`–`(A6)`; `App. B`: `Eqs. (B1)`–`(B10)`), Tables I–II, all 57 `\label` targets, all 32 `\cite{...}` calls (48 individual key citations), and all 22 inline `\bibitem` entries. Every analytical derivation and table entry was independently verified symbolically and numerically.

**Summary Verdict:** The manuscript's core algebraic contribution—the exact $(p+1)$-term closed-form expansion $c_{l,p}(R)$ for Laguerre--Gaussian ($\mathrm{LG}_{p,l}$) modes in Eqs. (31)–(33) and the intermediate hypergeometric algebra in Appendix B—is **exact to machine precision ($< 10^{-13}$)**. However, the manuscript suffers from **18 mathematical, operator-theoretic, and numerical defects (`R2-M1`–`R2-M18`)**, **13 structural, LaTeX, and editorial defects (`R2-E1`–`R2-E13`)**, and **10 bibliographic and citation defects (`R2-B1`–`R2-B10`)** that must be systematically corrected before publication.

---

## Section I: Mathematical, Theoretical & Numerical Audit (`R2-M1`–`R2-M18`)

### `R2-M1` — Misidentified Normalization Constant $C_0$ and Boundary Behavior at $R = 0$
- **Location:** Sec. II.A, L68–78 (`Eqs. (1)`–`(2)`, `eq:pvb_mode`, `eq:C0_norm`), L129–132 (`Eq. (9)`, `eq:overlap_closed`), App. A L431–436 (`Eq. (A6)`).
- **Observation:** L74 calls $C_0 = \frac{1}{w^2}\sqrt{\frac{2}{\pi}}$ *"the normalization constant"*.
- **Audit Finding:** $\Phi_{l,R}$ is **not** $L^2(\mathbb{R}^2)$-normalized. Using Eq. (9) at $R = R' = 2.0$, $w = 0.5$, $l = 1$ gives $\|\Phi_{1,2}\|_{L^2}^2 = \frac{1}{w^2}e^{-R^2/w^2}I_{|l|}(R^2/w^2) = 0.389398459026 \neq 1$ (confirmed by direct numerical radial integration to $1.67 \times 10^{-16}$). Furthermore, $\Phi_{l,R}$ has physical dimensions $[\text{length}^{-2}]$ rather than $[\text{length}^{-1}]$. The constant $C_0$ is the **continuous-frame resolution-of-identity scaling factor** chosen so that the frame operator $S_w$ under measure $d\mu(R) = R\,dR$ satisfies $B = 1$ (dimensionless). In addition, L68 includes $R = 0$ in $R \in [0,\infty)$, yet for any $l \neq 0$, $\Phi_{l,0}(r,\phi) \equiv 0$ identically (while $\|\Phi_{0,0}\|^2 = 1/w^2$).
- **Required Fix:** Explicitly identify $C_0$ as the resolution-of-identity scaling factor (retaining $B=1$) and contrast it with unit-normalized modes $\psi_{l,R} = \Phi_{l,R}/\|\Phi_{l,R}\|_{L^2}$; restrict the annular regime to $R > 0$ (noting the degenerate $R=0, l=0$ Gaussian limit separately).

### `R2-M2` — Incomplete Asymptotic Validity Conditions for Eq. (3)
- **Location:** Sec. II.A, L80–84 (`Eq. (3)`, `eq:pvb_asymptotic`).
- **Observation:** L80 asserts that $I_l(x) \approx e^x/\sqrt{2\pi x}$ holds when *"($R \gg w$) and $|l| \ll R/w$"*.
- **Audit Finding:** The algebraic prefactor $\frac{C_0}{\sqrt{4\pi R r/w^2}} = \frac{1}{\sqrt{2\pi^2 R r w^2}}$ is exact. However, Hankel's second-order correction is $-\frac{4l^2 - 1}{8x}$ with $x = 2Rr/w^2 \approx 2R^2/w^2$ on the ring, so $|4l^2 - 1|/(8x) \ll 1$ corresponds to $|l| \ll 2R/w$ (for example, at $R/w = 4$, $x = 32$, $l = 4$, the leading-order error is already $28.37\%$). Moreover, Eq. (3) diverges as $r^{-1/2}$ as $r \to 0$, whereas exact Eq. (1) vanishes as $r^{|l|}$, so Eq. (3) is valid only away from the origin ($r \sim R \gg w$).
- **Required Fix:** State the uniform validity regime $r \sim R \gg w$ and $|l| \ll 2R/w$ (or $l^2 \ll 4Rr/w^2$).

### `R2-M3` — Axicon Apex vs. Base (Wedge) Angle Error
- **Location:** Sec. II.B, L94 (`Eq. (4)`, `eq:bg_field`).
- **Observation:** L94 writes *"axicon with refractive index $n_{\text{ax}}$ and apex angle $\alpha_{\text{ax}}$, $k_r = k (n_{\text{ax}} - 1)\alpha_{\text{ax}}$"*.
- **Audit Finding:** In thin-axicon / paraxial refraction, the deflection angle is $(n_{\text{ax}} - 1)\beta$, where $\beta$ is the **base (wedge) angle**, not the **apex angle** ($\alpha_{\text{apex}} = \pi - 2\beta$).
- **Required Fix:** Replace apex angle $\alpha_{\text{ax}}$ with base (wedge) angle $\beta$ (also eliminating the symbol clash with Tikhonov $\alpha$).

### `R2-M4` — Symbol Collision on $k$ and Undefined Cutoff Transition $k_{\text{paraxial}} \to k_{\max}$
- **Location:** Sec. II.B L94, L98 (`Eq. (5)`, `eq:fourier_parameters`) vs. Sec. III.B–C L168, L184–188 (`Eq. (17)`, `eq:paley_wiener`).
- **Observation:** L94 and L98 denote the optical wavenumber $2\pi/\lambda$ by $k$, whereas L168 defines $k = |\mathbf{k}|$ as the transverse spatial frequency, and L184 shifts notation to $k_0 = 2\pi/\lambda$ alongside an undefined $k_{\text{paraxial}}$ that immediately becomes $k_{\max}$ in Eq. (17).
- **Required Fix:** Use $k_0 = 2\pi/\lambda$ consistently for the optical wavenumber (fixing Eq. (5) to $R = k_r f/k_0$, $w = 2f/(k_0 w_g)$) and reserve $k_\perp = |\mathbf{k}|$ (or $k = |\mathbf{k}|$) strictly for transverse spatial frequency with $k_{\max} = k_0 \mathrm{NA}$.

### `R2-M5` — Index Typo $I_l$ Instead of $I_{l'}$ in Eq. (6)
- **Location:** Sec. III.A, L110–115 (`Eq. (6)`, `eq:overlap_start`).
- **Observation:** L113 writes $I_l\left(\frac{2Rr}{w^2}\right) I_l\left(\frac{2R'r}{w^2}\right)$ prior to evaluating the azimuthal orthogonality integral Eq. (7).
- **Audit Finding:** Before setting $l' = l$ via Eq. (7), the second modified Bessel factor belonging to $\Phi_{l',R'}$ must carry index $l'$, i.e., $I_{l'}(2R'r/w^2)$.
- **Required Fix:** Correct the second Bessel order in Eq. (6) to $I_{l'}(2R'r/w^2)$.

### `R2-M6` — Missing Gradshteyn--Ryzhik Formula Number, Hypotheses, and $I_l = I_{|l|}$ Symmetry in Weber's Integral
- **Location:** Sec. III.A, L122–127 (`Eq. (8)`, `eq:weber_identity`); App. A L420–424 (`Eq. (A2)`).
- **Observation:** Cites *"Weber's exponential integral relation~\cite{gradshteyn2014table}"* without formula number, convergence conditions, or negative-$l$ justification.
- **Audit Finding:** The standard identity is Gradshteyn & Ryzhik **6.633.2** (analytically continued from $J_\nu$ via $J_\nu(ix) = i^\nu I_\nu(x)$), which requires $\operatorname{Re}(p) > 0$ and $\operatorname{Re}(\nu) > -1$. For integer $l < 0$, $\operatorname{Re}(l) \le -1$ violates the hypothesis unless one invokes $I_l(x) = I_{|l|}(x)$ for $l \in \mathbb{Z}$.
- **Required Fix:** Cite G&R **6.633.2**, state $\operatorname{Re}(p) > 0$ and $\operatorname{Re}(\nu) > -1$, and explicitly apply $I_l(x) = I_{|l|}(x)$ before evaluating the integral.

### `R2-M7` — Outsourced Kernel Proof ($S_w = G_w * \cdot$) and Undefined Fourier Convention
- **Location:** Sec. III.B–C, L150–176 (`Eqs. (12)`–`(15)`).
- **Observation:** L150 outsources the central convolution identity $S_w \psi = G_w * \psi$ to Appendix D of Ref.~\cite{ferreira2026second}, and L162 introduces $\widetilde{\psi}(\mathbf{k}) = \mathcal{F}\{\psi\}(\mathbf{k})$ without defining the normalization convention.
- **Audit Finding:** Writing $\widetilde{\psi}(\mathbf{k}) = \int_{\mathbb{R}^2} \psi(\mathbf{r}) e^{-i\mathbf{k}\cdot\mathbf{r}} d^2\mathbf{r}$ makes both Eq. (14) ($\widetilde{G}_w(k) = e^{-w^2 k^2/2}$) and the $(2\pi)^{-2}$ Plancherel weight in Eq. (15) exact; omitting this definition leaves a potential $(2\pi)$ factor ambiguity. Moreover, the kernel theorem $S_w = G_w * \cdot$ takes only 3 lines in Fourier space via $\widetilde{\Phi}_{l,R}(\mathbf{k}) = \sqrt{2\pi}(-i)^{|l|} e^{il\phi_k} e^{-w^2 k^2/4} J_{|l|}(Rk)$ (verified numerically to $4.2 \times 10^{-16}$) and Hankel closure $\int_0^\infty R\,dR\, J_{|l|}(Rk)J_{|l|}(Rk') = \delta(k-k')/k$, or in position space via Weber's integral and Jacobi--Anger (verified numerically to $2.25 \times 10^{-10}$).
- **Required Fix:** Define the non-unitary 2D Fourier transform convention explicitly and include the self-contained 3-line proof of $S_w = G_w * \cdot$ directly in Sec. III.B (replacing the redundant Appendix A).

### `R2-M8` — Non-Existence of Unprojected $S_w^{-1}\Phi_{l,R} \in L^2(\mathbb{R}^2)$ and Unproved Sharpness of $A, B$
- **Location:** Sec. III.C–IV.A, L184–204 (`Eqs. (17)`–`(20)`), L211, L246–250 (`Eq. (27)`).
- **Observation:** L195 asserts *"optimal bounds"* $A(w,k_{\max}) = e^{-w^2 k_{\max}^2/2}, B = 1$ without proof, and L211 writes the unregularized canonical dual frame as $\widetilde{\Phi}_{l,R} = S_w^{-1}\Phi_{l,R}$.
- **Audit Finding:** (a) Optimality/sharpness of $A$ and $B$ requires exhibiting saturating bandlimited test wavepackets in $\mathcal{H}_{k_{\max}}$ localized in Fourier rings near $|\mathbf{k}| \to 0^+$ (giving $B = 1$) and $|\mathbf{k}| \to k_{\max}^-$ (giving $A = e^{-w^2 k_{\max}^2/2}$). (b) More fundamentally, because $\widetilde{\Phi}_{l,R}(\mathbf{k}) \propto e^{-w^2 k^2/4} J_{|l|}(Rk)$ is **not** bandlimited, $\Phi_{l,R} \notin \mathcal{H}_{k_{\max}}$, and multiplying by $\widetilde{G}_w^{-1}(k) = e^{+w^2 k^2/2}$ yields $\widetilde{G}_w^{-1}\widetilde{\Phi}_{l,R} \propto e^{+w^2 k^2/4} J_{|l|}(Rk) \notin L^2(\mathbb{R}^2)$. Therefore, **the unprojected dual mode $S_w^{-1}\Phi_{l,R}$ at L211 does not exist in $L^2(\mathbb{R}^2)$**. On $\mathcal{H}_{k_{\max}}$, the frame must be projected as $\{P_{k_{\max}}\Phi_{l,R}\}$ with canonical dual $(P_{k_{\max}} S_w P_{k_{\max}})^{-1} P_{k_{\max}}\Phi_{l,R} \in \mathcal{H}_{k_{\max}}$.
- **Required Fix:** Explicitly construct the saturating sequences proving sharpness of $A$ and $B$, introduce the bandlimit projector $P_{k_{\max}}$ on $\mathcal{H}_{k_{\max}}$, and state that unprojected $S_w^{-1}\Phi_{l,R} \notin L^2(\mathbb{R}^2)$.

### `R2-M9` — Unspecified Space $\mathcal{H}$, Missing Synthesis Formula, and False *"Without Distortion"* Claim for $\alpha > 0$
- **Location:** Sec. IV.A–B, L228–251 (`Eqs. (24)`–`(27)`), L299.
- **Observation:** Eq. (24) minimizes over $\psi \in \mathcal{H}$ without specifying $\mathcal{H}$, omits the explicit dual synthesis equation, and L299 claims modes can be *"reconstructed without distortion on $\mathcal{H}_{k_{\max}}$ through the regularized dual frame modes $\widetilde{\Phi}_{l,R}^{(\alpha)}$"*.
- **Audit Finding:** (a) In Eq. (24), $\mathcal{H}$ should be specified as $L^2(\mathbb{R}^2)$ or $\mathcal{H}_{k_{\max}}$. (b) The explicit regularized reconstruction $\psi_{\text{rec}}^{(\alpha)} = \sum_l \int_0^\infty R\,dR\, \braket{\Phi_{l,R}}{\psi} \widetilde{\Phi}_{l,R}^{(\alpha)} = S_{w,\alpha}^{-1} S_w \psi$ has Fourier multiplier $\frac{\widetilde{G}_w^2(k)}{\widetilde{G}_w^2(k) + \alpha}$, whereas direct deconvolution of noisy measurements $\psi_{\text{meas}} = S_w\psi + \eta$ via $S_{w,\alpha}^{-1}\psi_{\text{meas}}$ applies $\frac{\widetilde{G}_w^2}{\widetilde{G}_w^2+\alpha}$ to $\psi$ and $\widetilde{H}_{w,\alpha}$ to $\eta$. (c) **L299 is mathematically false for any $\alpha > 0$:** since $\frac{\widetilde{G}_w^2(k)}{\widetilde{G}_w^2(k) + \alpha} < 1$ strictly on $\mathcal{H}_{k_{\max}}$, Tikhonov regularization inevitably introduces high-frequency attenuation (shrinkage bias). Exact distortionless reconstruction holds **only** at $\alpha = 0$ on $\mathcal{H}_{k_{\max}}$ using the projected canonical dual frame.
- **Required Fix:** Specify $\mathcal{H}$, display the explicit regularized synthesis/deconvolution operator multipliers, and replace L299 with an accurate statement of the $\alpha = 0$ exactness on $\mathcal{H}_{k_{\max}}$ vs. the $\alpha > 0$ bias--variance trade-off.

### `R2-M10` — Symbol Collision on $\alpha$
- **Location:** Sec. IV.A L232 (`Eqs. (24)`–`(27)`) vs. Sec. IV.B L275 & App. B L444–495.
- **Observation:** $\alpha$ denotes both the dimensionless Tikhonov regularization parameter (L232) and the dimensional Gaussian exponent $\alpha = 1/w^2 + 1/w_0^2$ in $[\text{length}^{-2}]$ (L275, L448).
- **Required Fix:** Rename the Gaussian exponent in Sec. IV.B / App. B to $a_0$ (or $\alpha_0$) while keeping $\alpha_{\text{reg}}$ (or $\alpha$) exclusively for Tikhonov regularization.

### `R2-M11` — Wrong G&R Formula Number (`6.643.2`), Missing $I_l = I_{|l|}$, Ferreira Normalization Gap, and Bare `$LG_{p,l}$`
- **Location:** Sec. IV.B L278–300 (`Eqs. (28)`–`(34)`); App. B L438–503 (`Eqs. (B1)`–`(B10)`).
- **Audit Finding:** Symbolic (`SymPy`) and numerical quadrature checks across $(p,l) \in \{(0,0),(0,2),(1,1),(2,-2),(3,1),(4,-3)\}$ confirm that **Eqs. (31)–(33) and the algebraic steps in App. B L442–502 are exact** (max numerical discrepancy $9.70 \times 10^{-14}$ for $c_{l,p}(R)$ and $1.67 \times 10^{-16}$ for Eq. (34)). However, four defects appear:
  1. **Wrong G&R Formula (L461):** Cites formula **`6.643.2`** (which is the Whittaker-$M$ integral of $x^{\mu-1/2}e^{-\alpha x}I_{2\nu}(2\beta\sqrt{x})$) instead of **`6.631.1`** ($\int_0^\infty x^{\mu-1} e^{-\alpha x^2} J_\nu(\beta x)\,dx$, analytically continued via $J_\nu(i\beta x) = i^\nu I_\nu(\beta x)$).
  2. **Negative-$l$ Omission (L445, L457, L468):** Uses $I_l(\beta r)$ prior to setting $\nu = |l|$ at L466 without explicitly invoking $I_l(\beta r) = I_{|l|}(\beta r)$ for $l \in \mathbb{Z}$.
  3. **Imprecise Recovery Claim (L294):** Claims Eq. (31) at $p=0$ *"immediately recover[s] the result of Ferreira et al.~\cite{ferreira2026second}"*, overlooking that Ferreira *et al.* normalize each mode to unit $L^2$ norm via $N_{|l|}$, differing from $C_0 = \sqrt{2/\pi}/w^2$ by $1/\|\Phi_{l,R}\|_{L^2}$.
  4. **Typography (L296 & 9 other lines):** Writes `$LG_{p,l}$` inside math mode (`L\cdot G_{p,l}`).
- **Required Fix:** Change `6.643.2` $\to$ `6.631.1`, state $I_l = I_{|l|}$ explicitly, note the $C_0$ vs. $N_{|l|}$ scaling factor at L294, and replace `$LG_{p,l}$` with `\mathrm{LG}_{p,l}` / `\psi_{p,l}`.

### `R2-M12` — Numerical Errors in Table I (up to $-0.02241$) and Defective Radial Rayleigh Threshold Eq. (37)
- **Location:** Sec. IV.C, L310–338 (`Eqs. (36)`–`(37)`, Table I `tab:fidelity`).
- **Audit Finding (Table I):** Exact Fourier-space evaluation of Eq. (36),
  $$\mathcal{F}(p,l,w/w_0) = \frac{\left(\int_0^\infty e^{-a u}\,\rho_{p,l}(u)\,du\right)^2}{\int_0^\infty e^{-2a u}\,\rho_{p,l}(u)\,du}, \qquad a = \frac{w^2}{w_0^2},\quad \rho_{p,l}(u) = \frac{p!}{(p+|l|)!}\,u^{|l|} e^{-u}\left[L_p^{|l|}(u)\right]^2,$$
  verified both by `scipy.integrate.quad` (matching 2D spatial integration to $10^{-10}$) and exact `SymPy` rational arithmetic at $w/w_0 = 1.00$, reveals systematic errors across Table I up to **$-0.02241$**:

| $w/w_0$ | $p=0$ (`p3_3` $\to$ Exact) | $p=1$ (`p3_3` $\to$ Exact) | $p=2$ (`p3_3` $\to$ Exact) | $p=3$ (`p3_3` $\to$ Exact) |
|---|---|---|---|---|
| $0.05$ | $0.99999 \to \mathbf{0.99999}$ | $0.99995 \to \mathbf{0.99995}$ | $0.99988 \to \mathbf{0.99989}$ | $0.99972 \to \mathbf{0.99980}$ |
| $0.10$ | $0.99980 \to \mathbf{0.99980}$ | $0.99921 \to \mathbf{0.99921}$ | $0.99821 \to \mathbf{0.99822}$ | $0.99673 \to \mathbf{0.99683}$ |
| $0.20$ | $0.99704 \to \mathbf{0.99704}$ | $0.98783 \to \mathbf{0.98782}$ | $0.97290 \to \mathbf{0.97282}$ | $0.95379 \to \mathbf{0.95276}$ |
| $0.40$ | $0.96231 \to \mathbf{0.96231}$ | $0.84951 \to \mathbf{0.84935}$ | $0.72564 \to \mathbf{0.72301}$ | $0.62993 \to \mathbf{0.61610}$ |
| $0.60$ | $0.86486 \to \mathbf{0.86477}$ | $0.58408 \to \mathbf{0.58216}$ | $0.45049 \to \mathbf{0.43953}$ | $0.38393 \to \mathbf{0.36419}$ |
| $0.80$ | $0.71990 \to \mathbf{0.71861}$ | $0.40750 \to \mathbf{0.39960}$ | $0.32789 \to \mathbf{0.30831}$ | $0.27102 \to \mathbf{0.26129}$ |
| $1.00$ | $0.57033 \to \mathbf{0.56250}\;(\tfrac{9}{16})$ | $0.33510 \to \mathbf{0.31641}\;(\tfrac{81}{256})$ | $0.26622 \to \mathbf{0.24381}\;(\tfrac{18225}{74752})$ | $0.20236 \to \mathbf{0.20681}\;(\tfrac{8037225}{38862848})$ |

- **Audit Finding (Eq. (37)):** The heuristic $w \lesssim 0.2\,w_0/\sqrt{p}$ (L336) is singular at $p = 0$, omits $|l|$, and contradicts Table I at $p = 3, w/w_0 = 0.20$ ($\mathcal{F} = 0.95276 > 0.95$ despite $0.20 > 0.2/\sqrt{3} = 0.115$). Expanding $\mathcal{F} = 1 - a^2 \operatorname{Var}(U) + O(a^3)$ with $\operatorname{Var}(U) = 2p^2 + 2p|l| + 2p + |l| + 1 \approx \frac{1}{2}(2p+|l|+1)^2$ ($p \ge 1$) gives the leading 2nd-cumulant Taylor estimate
  $$w_{\text{crit}}^{(2)}(p, l) \approx \frac{(0.10)^{1/4}}{\sqrt{2p + |l| + 1}}\, w_0 \approx \frac{0.5623}{\sqrt{2p + |l| + 1}}\, w_0 \quad (p \ge 1).$$
  Because higher-order cumulants shift the exact $\mathcal{F}=0.95$ root slightly upward, the exact $p \to \infty$ arcsine-law asymptote $\mathcal{F} \to I_0(c)^2/I_0(2c) = 0.95$ with $c = a(2p+|l|+1) = 0.327687$ yields $\sqrt{c} = 0.57244$, while direct root-finding (`brentq` on exact `SymPy` rational expressions at $l=1$) gives $w_{\text{crit}}\sqrt{2p+|l|+1} = 0.5806, 0.5759, 0.5744, 0.5727$ for $p = 1, 2, 3, 10$, justifying the moderate-$p$ ($p=1\text{--}10$) scaling
  $$w_{\text{crit}}(p, l) \approx \frac{0.573}{\sqrt{2p + |l| + 1}}\, w_0 \quad (p \ge 1).$$
  For $p = 0$, exact integration gives $\mathcal{F}(0,l,w/w_0) = [(1+2a)/(1+a)^2]^{|l|+1}$, yielding the exact closed-form threshold
  $$w_{\text{crit}}(0, l) = \left[\left(1 - 0.95^{1/(|l|+1)}\right)^{-1/2} - 1\right]^{-1/2} w_0,$$
  which equals $0.5367\,w_0$ at $l=0$ and $0.4350\,w_0$ at $l=1$ (note that the leading-order Taylor truncation $[0.05/(|l|+1)]^{1/4} w_0$ underestimates this exact threshold by $11.9\%$ at $l=0$ and $8.6\%$ at $l=1$).
- **Required Fix:** Replace Table I with the exact recomputed values and replace Eq. (37) with the verified $(2p+|l|+1)^{-1/2}$ law for $p \ge 1$ alongside the exact closed-form threshold for $p = 0$.

### `R2-M13` — Five Compounded Errors in Table II and Gram Conditioning Claims
- **Location:** Sec. IV.D, L347–381 (`Eqs. (39)`–`(41)`, Table II `tab:gram_matrix`); Abstract L35; Conclusions L406.
- **Audit Finding:** Cross-checking Table II ($N = 6, w = 0.5, l = 1, R_{\min} = 2.0$) exposes five compounded errors:
  1. **Unnormalized $G_{nm}$ vs. Normalized $\gamma_{nm}$ Conflation:** Table II reports $\kappa(G)$ for the **unnormalized** Gram matrix $G_{nm}$ whose diagonal decays as $G_{nn} \approx 1/(\sqrt{2\pi} R_n w)$. As $\Delta R/w$ increases past $2.0$, $R_6/R_1$ grows, causing $\kappa(G)$ to **increase** ($3.959 \to 4.096 \to 4.646$) even as the channels decouple, whereas the true normalized Gram matrix $\gamma_{nm}$ converges monotonically ($\kappa(\gamma) = 1.645 \to 1.172 \to 1.041 \to 1$).
  2. **Condition Number Self-Contradiction:** L377 claims *"For $\Delta R < 1.5\,w$, the matrix is ill-conditioned ($\kappa > 10^4$)"*, contradicting Table II's own entry $\kappa(G) = 34.3$ at $\Delta R/w = 1.00$ ($\kappa > 10^4$ holds only at $\Delta R/w = 0.50$, where $\kappa(G) = 1.123\times 10^4$ and $\kappa(\gamma) = 1.086\times 10^4$).
  3. **Crosstalk Threshold Self-Contradiction:** Abstract L35, L377, and Conclusions L406 claim *"$\le 13.5\%$"* / *"below $13.5\%$"*, whereas Table II prints `13.6%` at $\Delta R/w = 2.00$ (exact $\gamma_{12} = 13.553\%$; asymptotic $e^{-2} = 13.534\%$).
  4. **False $\kappa(G) < 50$ Bound for Large $N$:** Because $\kappa(G) \propto R_{\max}/R_{\min}$, the Abstract/Conclusions claim $\kappa(G) < 50$ fails whenever $R_{\max} > 50 R_{\min}$ (verified at $N = 120, \Delta R/w = 2.0$: $\kappa(G) = 80.015$, whereas $\kappa(\gamma) = 1.741$).
  5. **Amplitude vs. Power Crosstalk Confusion:** At $\Delta R/w = 2.50$, $|\gamma_{12}| = 4.402\%$ is a **field amplitude** overlap whose **power crosstalk** is $|\gamma_{12}|^2 = 0.1938\%$ (**$27.13\,\text{dB}$** power isolation). L377 writes `"crosstalk < 4.4% (isolation > 13.5 dB)"`, erroneously applying $-10\log_{10}(0.044)$ to an amplitude ratio.

| $\Delta R/w$ | $\gamma_{12}$ (Amp.) | $\lvert \gamma_{12}\rvert^2$ (Power) | Power Iso. (dB) | $\kappa(G)$ (`p3_3`) | $\kappa(\gamma)$ (Norm.) | $\frac{1}{N}\operatorname{Tr}(\gamma^{-1})$ | $\frac{1}{N}\operatorname{Tr}(\gamma^{-2})$ |
|---|---|---|---|---|---|---|---|
| $0.50$ | $88.26\%$ | $77.91\%$ | $1.08$ | $1.123 \times 10^4$ | $1.086 \times 10^4$ | $501.99$ ($27.01\,\text{dB}$) | $1.364\times 10^6$ ($61.35\,\text{dB}$) |
| $1.00$ | $60.68\%$ | $36.83\%$ | $4.34$ | $34.3$ | $28.80$ | $3.418$ ($5.34\,\text{dB}$) | $30.14$ ($14.79\,\text{dB}$) |
| $1.50$ | $32.50\%$ | $10.56\%$ | $9.76$ | $5.96$ | $3.723$ | $1.237$ ($0.92\,\text{dB}$) | $1.890$ ($2.76\,\text{dB}$) |
| $2.00$ | $13.55\%$ | $1.84\%$ | $17.36$ | $3.959$ | $1.645$ | $1.032$ ($0.14\,\text{dB}$) | $1.099$ ($0.41\,\text{dB}$) |
| $2.50$ | $4.40\%$ | $0.194\%$ | $27.13$ | $4.096$ | $1.172$ | $1.003$ ($0.01\,\text{dB}$) | $1.010$ ($0.04\,\text{dB}$) |
| $3.00$ | $1.11\%$ | $0.012\%$ | $39.07$ | $4.646$ | $1.041$ | $1.000$ ($0.00\,\text{dB}$) | $1.001$ ($0.00\,\text{dB}$) |

- **Required Fix:** Base Table II and all conditioning bounds on the **normalized** Gram matrix $\gamma_{nm}$ (retaining $\kappa(G)$ only as an explanatory contrast), separate amplitude overlap $|\gamma_{12}|$ from power crosstalk $|\gamma_{12}|^2$ (dB), and harmonize all text thresholds (`13.6%` at $2w$, $\kappa > 10^4$ at $\Delta R \le 0.5w$).

### `R2-M14` — Omitted $2f$ Chirp Cancellation, Gouy/Fourier Phase, and Power Scaling in Eq. (5)
- **Location:** Sec. II.B, L96–100 (`Eq. (5)`, `eq:fourier_parameters`).
- **Audit Finding:** Claiming that a lens of focal length $f$ yields Eq. (1) omits: (i) exact $2f$ placement ($d_{\text{in}} = f$ before the lens) required to cancel the residual quadratic phase chirp $\exp[i k_0 r^2(1 - d_{\text{in}}/f)/(2f)]$; (ii) the topological-charge-dependent $2f$ Fourier phase factor $(-i)^{l+1} e^{2i k_0 f}$ from using signed $J_l(k_r\rho)$ in Eq. (4) (becoming $(-i)^{|l|+1} e^{2i k_0 f}$ only if $J_{|l|}(k_r\rho)$ is adopted); and (iii) the fact that the unnormalized Bessel--Gauss input Eq. (4) yields focal prefactor $\propto w_g/w \propto w^{-1}$ rather than $C_0 \propto w^{-2}$ unless rescaled by input beam power.
- **Required Fix:** State the $2f$ Fourier geometry, overall phase factor, and amplitude-scaling convention.

### `R2-M15` — Incorrect High-Frequency Decay Threshold in Tikhonov Filter Eq. (26)
- **Location:** Sec. IV.A, L251 (`Eq. (26)`, `eq:tikhonov_filter`).
- **Observation:** L251 states *"when $k \gg 1/w$, $\widetilde{H}_{w,\alpha}(k) \to \frac{1}{\alpha}\exp(-w^2 k^2/2) \to 0$"*.
- **Audit Finding:** For small regularization $\alpha \ll 1$, $\widetilde{H}_{w,\alpha}(k)$ actually **grows** as $e^{+w^2 k^2/2}$ well past $k = 1/w$, peaking at $\widetilde{H}_{\max} = \frac{1}{2\sqrt{\alpha}}$ when $k_{\text{peak}} = \frac{1}{w}\sqrt{\ln(1/\alpha)}$ (e.g., for $\alpha = 10^{-4}, w = 0.5$, $k_{\text{peak}} = 6.070 \gg 1/w = 2.0$ with $\widetilde{H}_{\max} = 50.0$). Exponential decay requires $e^{-w^2 k^2} \ll \alpha$, i.e., $k \gg \frac{1}{w}\sqrt{\ln(1/\alpha)}$.
- **Required Fix:** Correct the decay crossover condition at L251 to $k \gg w^{-1}\sqrt{\ln(1/\alpha)}$ and report the peak gain $(2\sqrt{\alpha})^{-1}$.

### `R2-M16` — Misstated $\mathrm{LG}_{p,l}$ Ring Radius Scaling at L45
- **Location:** Sec. I, L45.
- **Observation:** L45 writes *"the radius of the primary bright intensity ring scales monotonically with the topological charge as $r_{\text{max}} \sim w_0\sqrt{2p+|l|+1}$"*.
- **Audit Finding:** At $p=0, l=0$, the intensity peak is on-axis ($r_{\max} = 0$); for $p=0, |l|\ge 1$, the ring peak is $r_{\text{peak}} = w_0\sqrt{|l|/2}$; and for $p \ge 1$, the brightest (innermost) ring actually shrinks with $p$ ($0.468\,w_0$ at $p=1,l=1$ vs. $0.379\,w_0$ at $p=2,l=1$). Rather, $w_0\sqrt{2p+|l|+1}$ is the **RMS beam radius** $r_{\text{rms}}$ (second-moment radius, or outer caustic).
- **Required Fix:** Replace $r_{\text{max}}$ with the RMS beam radius $r_{\text{rms}} = w_0\sqrt{2p+|l|+1}$ (noting $r_{\text{peak}} = w_0\sqrt{|l|/2}$ for $p=0, |l|\ge 1$).

### `R2-M17` — Silent Asymptotic Core Assumption in Eqs. (40)–(41)
- **Location:** Sec. IV.D, L353–381 (`Eqs. (40)`–`(41)`, `eq:crosstalk_asymptotic`, `eq:channel_capacity`).
- **Audit Finding:** Both $\gamma_{n,n+1} \approx e^{-\Delta R^2/(2w^2)}$ and $N_{\max} \approx \lfloor \mathcal{W}/(2w) \rfloor + 1$ rely on the large-argument Hankel asymptotic $R_{\min} \gg w, |l|w/2$ (`R2-M2`). Near the core ($R_{\min} = 0.2w, l=1, \Delta R = 2.0w$), exact $\gamma_{12} = 34.76\%$ vs. $e^{-2} = 13.53\%$.
- **Required Fix:** Explicitly qualify Eqs. (40)–(41) with the annular regime $R_{\min} \gg w, |l|w/2$.

### `R2-M18` — Unquantified SDM Zero-Forcing Noise Penalty at L391
- **Location:** Sec. V.A, L391.
- **Observation:** Claims *"demultiplexing via Zero-Forcing or MMSE equalization with minimal noise penalty"* without any calculation.
- **Audit Finding:** Evaluating ZF noise enhancement on the normalized Gram matrix $\gamma_{nm}$ ($N=6, w=0.5, l=1, R_{\min}=2.0$) requires distinguishing two physically distinct noise models:
  - **Correlated projection noise** ($\mathbb{E}[\eta\eta^\dagger] = \sigma^2 \gamma$, frame sampling noise): $\frac{1}{N}\operatorname{Tr}(\gamma^{-1}) = 1.0321$ ($0.14\,\text{dB}$) at $\Delta R/w = 2.0$, and $1.0032$ ($0.01\,\text{dB}$) at $\Delta R/w = 2.5$ (rising to $5.34\,\text{dB}$ at $\Delta R/w = 1.0$).
  - **Post-projection white AWGN** ($\mathbb{E}[\eta\eta^\dagger] = \sigma^2 I$, independent detector noise per output equalized via $\gamma^{-1}$): $\frac{1}{N}\operatorname{Tr}(\gamma^{-2}) = 1.0994$ ($0.41\,\text{dB}$) at $\Delta R/w = 2.0$, and $1.0097$ ($0.04\,\text{dB}$) at $\Delta R/w = 2.5$ (rising to $14.79\,\text{dB}$ at $\Delta R/w = 1.0$).
  Using unnormalized $G_{nm}$ instead induces strongly channel-dependent SNR degradation proportional to $R_n$.
- **Required Fix:** Quantify both normalized-Gram ZF noise-enhancement metrics explicitly in the revised Classical Optics Utility section.

---

## Section II: Structure, LaTeX & Scientific Writing Audit (`R2-E1`–`R2-E13`)

| ID | Exact Location (`p3_3/main.tex`) | Category | Direct Observation & Exact Counts | Corrective Action for `V6/` |
|---|---|---|---|---|
| **R2-E1** | `L1`, `L3–5`, `L10–15`, `L18–22` | Preamble & REVTeX Class | `L1` uses `twocolumn,superscriptaddress` with `longbibliography`: (a) `reprint` is the standard APS PRA 10 pt layout; (b) `superscriptaddress` is unnecessary for a single author; (c) `longbibliography` is defeated by inline `\thebibliography` (`L504–594`); (d) `\usepackage{graphicx}` (`L3`, 0 figures), `dcolumn` (`L4`, 0 `d` columns), and `bm` (`L5`, 0 `\bm` uses) are unused; (e) `\bra`, `\ket`, `\abs`, `\norm` (`L18–22`) are defined but never invoked; (f) `\hypersetup` omits `pdftitle`/`pdfauthor`. | Use `aps,pra,reprint,amsmath,amssymb,floatfix,longbibliography` for PRA (dropping `superscriptaddress`); prune unused packages/macros (or invoke `\norm`/`\abs` consistently); keep `graphicx` for the 3 figures; add `pdftitle`/`pdfauthor`; differentiate `main_arxiv.tex` (`onecolumn,notitlepage,11pt`). |
| **R2-E2** | `L28–30` | Author Metadata | Lists `sayala@udec.cl` and `Independent Researcher, Concepci\'on, Chile` without ORCID, conflicting with the author's verified contact/affiliation/ORCID (`ayala.phys.ds@gmail.com`, `Cauquenes, Chile`, ORCID `0009-0003-7348-3883`). | Reconcile author email, affiliation, and ORCID consistently across both `main_pra.tex` and `main_arxiv.tex`. |
| **R2-E3** | `L34–36` (Abstract), `L61`, `L406` | Abstract Density & Overclaiming | Abstract (`L35`) is **289 words** with **14 inline math tokens**, exceeding compact PRA limits; repeats false/erroneous bounds (`\kappa(G)<50`, `<13.5%`) and promises *"spatial quantum state tomography"* absent from Secs. II–V. | Tighten Abstract to $\le 220$ words with minimal symbols; ensure every classical and quantum claim aligns strictly with the revised body. |
| **R2-E4** | `L41–484` | Unused `\label`s (21 of 57) | Out of **57 `\label`s**, **21 are never referenced**: `sec:intro`, `eq:fourier_parameters`, `eq:gaussian_kernel`, `eq:plancherel`, `eq:paley_wiener`, `eq:transfer_bounds`, `eq:optimal_bounds`, `eq:cond_number`, `eq:noisy_meas`, `eq:tikhonov_op`, `eq:dual_modes`, `sec:analytic_lg_expansion`, `eq:lg_def`, `eq:dimensionless_params`, `eq:frame_synthesis_lg`, `eq:node_spacing`, `eq:fidelity_def`, `eq:discrete_radii`, `eq:gram_elements`, `app:weber`, `eq:app_int_term`. | Remove `app:weber`; cite key equations explicitly in prose and retain labels only for cross-referenced equations/sections. |
| **R2-E5** | `L417–501` | Unlabeled Appendix Equations | **9 display environments** in Appendices A & B (generating **11 numbered equations**: `Eqs. (A1)–(A6)` at `L417–436` and `Eqs. (B2), (B4), (B8)–(B10)` at `L451–501`) carry automatic numbers without `\label`s. | Remove App. A; use `align*` (or labeled numbered equations) for intermediate algebraic steps in the remaining appendix. |
| **R2-E6** | `L413–437` | Redundant Appendix A | `app:weber` is never cited anywhere and duplicates `Eqs. (8)–(13)` (`L122–132`) verbatim with trivial substitutions. | Delete `app:weber` entirely and reallocate space to the 3-line proof of $S_w = G_w * \cdot$ in Sec. III.B. |
| **R2-E7** | `L35, 45, 56, 61, 253, 256, 296, 303, 316, 441` | Bare `$LG_{p,l}$` Typography | 10 occurrences typeset `$LG_{p,l}$` (and `LG_{p,l}` in `Eq. (34)`) in math italics ($L\cdot G_{p,l}$). | Standardize to `\mathrm{LG}_{p,l}` for mode names and `\psi_{p,l}` in `Eq. (34)`. |
| **R2-E8** | `L47`, `L68`, `L391` | Acronyms & Definitions | (a) `POV` (`L47`) introduced once and never reused; (b) `$\Phi_{l,R}^{\text{ideal}} \propto \delta(r-R)e^{il\phi}$` omits the exact $1/(\sqrt{2\pi}\,R)$ normalization weight under the `Eq. (11)` measure $d\mu(R) = R\,dR$ (since $\int_0^\infty R\,dR\, \delta(r-R)\delta(r'-R)/(2\pi R^2) = \delta(r-r')/(2\pi r)$, whereas $1/\sqrt{2\pi R}$ corresponds to $dR$); (c) `R \in [0,\infty)` (`L68`) conflicts with $\Phi_{l\neq 0,0}\equiv 0$; (d) `MMSE` (`L391`) is undefined and `Zero-Forcing` is capitalized mid-sentence. | Drop `POV`, give the $1/(\sqrt{2\pi}\,R)$ Dirac weight for measure $R\,dR$, restrict rings to $R>0$, expand `minimum mean-square error (MMSE)`, and lowercase `zero-forcing`. |
| **R2-E9** | `L45` | Imprecise LG Radius | Writes $r_{\max} \sim w_0\sqrt{2p+\lvert l\rvert+1}$ (which is the **RMS** radius, not peak radius). | Replace with exact RMS radius $r_{\text{rms}} = w_0\sqrt{2p+\lvert l\rvert+1}$ and cite primary beam-optics literature. |
| **R2-E10** | `L35, 45, 56, 89, 134, 170, 184, 256, 353, 360, 371, 377, 404, 406` | Hyphenation, En-Dashes & Table II Style | Mixes `cross-talk`/`crosstalk`, `non-zero`/`nonzero`; uses single hyphens in `Laguerre-Gaussian`, `Paley-Wiener`, `Bessel-Gaussian`, and `non-orthogonal` (`L134`); Table II caption (`L360`) omits units for $w=0.5, R_{\min}=2.0$ and `L371` abbreviates `Quasi-ortho.`. | Standardize APS en-dashes (`--`), `crosstalk`, `nonzero`, specify dimensionless length units ($w_0$ or $\ell_0$) in Table II, and write `Quasi-orthogonal`. |
| **R2-E11** | `L383–400`, Whole MS | Underdeveloped Sec. V, 0 Figures, 0 Comparative Table | Sec. V (`sec:tradeoffs`) is 17 qualitative lines; 0 figures and 0 comparative tables appear in the manuscript. | Add quantitative Classical & Quantum Optics Utility subsections, 3 compact $2\times 2$ PDF figures, and 1 comparative table within $\le 10$ PRA pages. |
| **R2-E12** | `L408–410` | Missing Human–AI Attribution | Generic single-line acknowledgment omits APS-compliant disclosure of Human–AI collaboration. | Document collaboration between Sebastián Ayala and Gemini (in Antigravity IDE mode) in Acknowledgments + brief computational verification note per APS PRA policy. |
| **R2-E13** | `L378–381` | Unqualified $N_{\max}$ Bound | `Eq. (41)` states $N_{\max} \approx \lfloor \mathcal{W}/(2w) \rfloor + 1$ without stating its reliance on normalized $\gamma_{nm}$ ($\kappa(\gamma) \le 1.65$) and $R_{\min} \gg w$. | State both conditions explicitly when introducing $N_{\max}$. |

---

## Section III: Exhaustive Audit of All 22 Bibliography Entries & In-Text Citations (`R2-B1`–`R2-B10`)

### 3.1 Consolidated Bibliographic & Citation Findings (`R2-B1`–`R2-B10`)

1. **`R2-B1` (`L1`, `L504–594`) — Defeated `longbibliography` via Inline `\thebibliography`:** All 22 `\bibitem` entries omit article titles and DOIs, neutralizing the `longbibliography` class option on `L1`. **Fix:** Migrate to `V6/references.bib` + `\bibliographystyle{apsrev4-2}` with full titles, page ranges/article numbers, and DOIs.
2. **`R2-B2` (`L45, 96, 102, 389, 554–556`) — Critical Corruption & Misattribution in `aleman2023transmission`:** (i) Uses a non-existent key `aleman2023transmission` (no author named Alemán is on the paper); (ii) inverts author order (`S.~Ayala` placed 1st instead of 3rd after **N. Villalba** and **C. Melo**); (iii) at `L102`, misattributes the $>99.5\%$ theoretical coupling efficiency of Rojas-Rojas *et al.* (`rojas2021evaluating`, *Opt. Express* **29**, 23381, 2021) to this experimental 300 m RCF transmission paper (Villalba *et al.*, *Opt. Express* **31**, 40113, 2023, which measured $16\,\mu\text{W}/450\,\mu\text{W} \approx 3.6\%$ total link throughput and $6.83\,\text{dB}$ coupling gain over LG at $l=4$).
3. **`R2-B3` (`L47, 566–568`) — Malformed Author `C.~P.` in `reddy2016non` (+ Auxiliary Database Warning):** `reddy2016non` reduces second author **Chithrabhanu P.** (C. Perumangatt) to bare initials `C.~P.` without a surname. *Important Bibliographic Warning:* A corrupted `Reddy2016` record circulating in auxiliary `.bib` files (`v5/references.bib` `Reddy2016`) contains the wrong title (*"Divergence of Gaussian vortex beams"*), misspelled `"Permangatt"`, omitted coauthors (`P. Vaity`, `A. Aadhi`), and wrong coauthors (`A. Anwar`, `J. Banerji`); construct `Reddy2016` strictly from the verified *J. Opt.* **18**, 055602 (2016) record (`10.1088/2040-8978/18/5/055602`).
4. **`R2-B4` (`L122, 420, 461, 590–592`) — Wrong Gradshteyn & Ryzhik Formula Number:** `L461` cites `6.643.2` (Whittaker-$M$ transform of $x^{\mu-1/2}e^{-\alpha x}I_{2\nu}(2\beta\sqrt{x})$) instead of **`6.631.1`** (continued via $J_\nu(i\beta x) = i^\nu I_\nu(\beta x)$), and `L122, 420` omit the Weber formula number **`6.633.2`**.
5. **`R2-B5` (`L510–532`) — Premature `et al.` Truncation:** `bozinovic2013terabit` (8 authors), `mirhosseini2015high` (9 authors), and `bavaresco2018measurements` (8 authors) are manually truncated with `et al.` (whereas APS `apsrev4-2` prints up to 10 authors), and `willner2015optical` omits coauthors. Supply complete author lists in `V6/references.bib`.
6. **`R2-B6` (`L150, 294, 570–572`) — Over-Reliance on `ferreira2026second`:** `L150` outsources the 3-line $S_w = G_w * \cdot$ proof, and `L294` overlooks the $C_0$ vs. $N_{|l|}$ unit-normalization difference when recovering the $p=0$ case.
7. **`R2-B7` (`L53, 138, 582–584`) — Outdated Edition of Christensen:** `christensen2003introduction` cites the 1st ed. (2003); upgrade to the 2nd ed. (*An Introduction to Frames and Riesz Bases*, Birkhäuser, 2016, DOI `10.1007/978-3-319-25613-9`), which expands continuous frame theory.
8. **`R2-B8` (`L45, 538–540`) — Missing Primary Beam-Optics Reference at L45:** `walborn2010spatial` (an SPDC review) is cited for LG radius scaling; add Siegman's *Lasers* (`Siegman1986`) for the exact second-moment beam radius $r_{\text{rms}} = w_0\sqrt{2p+|l|+1}$.
9. **`R2-B9` (Sec. III, `L53, 138–188`) — Missing Seminal Frame, Coherent-State, RHS, and RKHS Citations:** Add `Daubechies1990` (*IEEE Trans. Inf. Theory* **36**, 961, 1990), `Klauder1985` (World Scientific, 1985), `Perelomov1986` (Springer, 1986) / `Gazeau2009` (Wiley-VCH, 2009), `Gelfand1964` (Academic Press, 1964), and `PaulsenRaghupathi2016` (Cambridge University Press, 2016).
10. **`R2-B10` (Sec. V / Optics Utility) — Missing RCF, Turbulence, and Quantum Tomography/SPDC Citations:** Add `Ramachandran2009` (*Opt. Lett.* **34**(16), 2525--2527, 2009), `Gregg2015` (*Optica* **2**, 267, 2015), `Paterson2005` (*Phys. Rev. Lett.* **94**, 153901, 2005), `TylerBoyd2009` (*Opt. Lett.* **34**, 142, 2009), `Renes2004` (*J. Math. Phys.* **45**, 2171, 2004), `LawEberly2004` (*Phys. Rev. Lett.* **92**, 127903, 2004), and `Cerf2002` (*Phys. Rev. Lett.* **88**, 127902, 2002).

### 3.2 Complete 22-Entry Reference Verification Table (`p3_3/main.tex` L506–592)

| # | `p3_3` Key | Lines (Bib / Cited) | Verified Published Record (Authors, Title, Venue, Vol(Iss), Pages, Year, DOI) | Audit Status |
|---|---|---|---|---|
| 1 | `allen1992orbital` | `L506–508` / `43, 45, 303` | L. Allen, M. W. Beijersbergen, R. J. C. Spreeuw, and J. P. Woerdman, *"Orbital angular momentum of light and the transformation of Laguerre-Gaussian laser modes"*, *Phys. Rev. A* **45**(11), 8185--8189 (1992), DOI `10.1103/PhysRevA.45.8185` | Core valid; missing title, end-page, DOI (`R2-B1`). |
| 2 | `willner2015optical` | `L510–512` / `43` | A. E. Willner *et al.* (17 authors), *"Optical communications using orbital angular momentum beams"*, *Adv. Opt. Photon.* **7**(1), 66--106 (2015), DOI `10.1364/AOP.7.000066` | Missing coauthors (`R2-B5`), title, end-page, DOI (`R2-B1`). |
| 3 | `wang2019twisted` | `L514–516` / `43` | J. Wang, *"Twisted optical communications using orbital angular momentum"*, *Sci. China Phys. Mech. Astron.* **62**(3), 034201 (2019), DOI `10.1007/s11433-018-9260-8` | Core valid; missing title, DOI (`R2-B1`). |
| 4 | `bozinovic2013terabit` | `L518–520` / `43` | N. Bozinovic, Y. Yue, Y. Ren, M. Tur, P. Kristensen, H. Huang, A. E. Willner, and S. Ramachandran, *"Terabit-scale orbital angular momentum mode division multiplexing in fibers"*, *Science* **340**(6140), 1545--1548 (2013), DOI `10.1126/science.1237861` | Premature `et al.` (`R2-B5`); missing title, end-page, DOI (`R2-B1`). |
| 5 | `padgett2011tweezers` | `L522–524` / `43` | M. Padgett and R. Bowman, *"Tweezers with a twist"*, *Nat. Photonics* **5**(6), 343--348 (2011), DOI `10.1038/nphoton.2011.81` | Core valid; missing title, end-page, DOI (`R2-B1`). |
| 6 | `mirhosseini2015high` | `L526–528` / `43` | M. Mirhosseini, O. S. Magaña-Loaiza, M. N. O'Sullivan, B. Rodenburg, M. Malik, M. P. J. Lavery, M. J. Padgett, D. J. Gauthier, and R. W. Boyd, *"High-dimensional quantum cryptography with twisted light"*, *New J. Phys.* **17**(3), 033033 (2015), DOI `10.1088/1367-2630/17/3/033033` | Premature `et al.` (`R2-B5`); missing title, DOI (`R2-B1`). |
| 7 | `bavaresco2018measurements` | `L530–532` / `43` | J. Bavaresco, N. Herrera Valencia, C. Klöckl, M. Pivoluska, P. Erker, N. Friis, M. Malik, and M. Huber, *"Measurements in two bases are sufficient for certifying high-dimensional entanglement"*, *Nat. Phys.* **14**, 1032--1037 (2018), DOI `10.1038/s41567-018-0203-z` | Premature `et al.` (`R2-B5`); missing title, end-page, DOI (`R2-B1`). |
| 8 | `erhard2018twisted` | `L534–536` / `43` | M. Erhard, R. Fickler, M. Krenn, and A. Zeilinger, *"Twisted photons: new quantum perspectives in high dimensions"*, *Light: Sci. Appl.* **7**, 17146 (2018), DOI `10.1038/lsa.2017.146` | Core valid; missing title, DOI (`R2-B1`). |
| 9 | `walborn2010spatial` | `L538–540` / `45, 303` | S. P. Walborn, C. H. Monken, S. Pádua, and P. H. Souto Ribeiro, *"Spatial correlations in parametric down-conversion"*, *Phys. Rep.* **495**(4--5), 87--139 (2010), DOI `10.1016/j.physrep.2010.06.003` | Core valid; add `Siegman1986` at `L45` (`R2-B8`); missing title, end-page, DOI (`R2-B1`). |
| 10 | `brunet2014design` | `L542–544` / `45` | C. Brunet, P. Vaity, Y. Messaddeq, S. LaRochelle, and L. A. Rusch, *"Design, fabrication and validation of an OAM fiber supporting 36 states"*, *Opt. Express* **22**(21), 26117--26127 (2014), DOI `10.1364/OE.22.026117` | Core valid; missing title, end-page, DOI (`R2-B1`). |
| 11 | `canas2021engineering` | `L546–548` / `45` | G. Cañas, E. S. Gómez, E. Baradit, G. Lima, and S. P. Walborn, *"Engineering Entangled Photons for Transmission in Ring-Core Optical Fibers"*, *Front. Phys.* **9**, 752081 (2021), DOI `10.3389/fphy.2021.752081` | Core valid; missing title, DOI (`R2-B1`). |
| 12 | `rojas2021evaluating` | `L550–552` / `45, 102, 389` | S. Rojas-Rojas, G. Cañas, G. Saavedra, E. S. Gómez, S. P. Walborn, and G. Lima, *"Evaluating the coupling efficiency of OAM beams into ring-core optical fibers"*, *Opt. Express* **29**(15), 23381--23392 (2021), DOI `10.1364/OE.425419` | Under-credited at `L102` (`R2-B2`); missing title, end-page, DOI (`R2-B1`). |
| 13 | `aleman2023transmission` | `L554–556` / `45, 96, 102(×3), 389` | N. Villalba, C. Melo, S. Ayala, C. Mancilla, W. Valenzuela, M. Figueroa, E. Baradit, R. Lin, M. Tang, S. P. Walborn, G. Lima, G. Saavedra, and G. Cañas, *"Transmission of optical communication signals through ring core fiber using perfect vortex beams"*, *Opt. Express* **31**(24), 40113--40123 (2023), DOI `10.1364/OE.503740` | **CRITICAL (`R2-B2`):** Wrong key, wrong author order (`S. Ayala` 1st instead of 3rd), misattributed `>99.5%` overlap at `L102`. |
| 14 | `ostrovsky2013generation` | `L558–560` / `47, 68` | A. S. Ostrovsky, C. Rickenstorff-Parrao, and V. Arrizón, *"Generation of the perfect optical vortex using a liquid-crystal spatial light modulator"*, *Opt. Lett.* **38**(4), 534--536 (2013), DOI `10.1364/OL.38.000534` | Core valid; missing title, end-page, DOI (`R2-B1`). |
| 15 | `vaity2015perfect` | `L562–564` / `47(×2), 68, 89, 96` | P. Vaity and L. Rusch, *"Perfect vortex beam: Fourier transformation of a Bessel beam"*, *Opt. Lett.* **40**(4), 597--600 (2015), DOI `10.1364/OL.40.000597` | Core valid; missing title, end-page, DOI (`R2-B1`). |
| 16 | `reddy2016non` | `L566–568` / `47` | S. G. Reddy, Chithrabhanu P., P. Vaity, A. Aadhi, S. Prabhakar, and R. P. Singh, *"Non-diffracting speckles of a perfect vortex beam"*, *J. Opt.* **18**(5), 055602 (2016), DOI `10.1088/2040-8978/18/5/055602` | **ERROR (`R2-B3`):** Malformed `C.~P.`; do NOT inherit corrupted `v5/references.bib` `Reddy2016`. |
| 17 | `ferreira2026second` | `L570–572` / `49(×3), 80, 150, 268, 294` | T. Ferreira, G. Santos, S. Ayala, L. Hutter, E. S. Gómez, G. Lima, G. Cañas, and S. P. Walborn, *"Second-order moment equivalence of twisted Gaussian Schell model beams and orbital angular momentum eigenmodes"*, *J. Opt.* **28**(9), 095601 (2026), DOI `10.1088/2040-8986/ae9b1d` | In-text over-reliance & $C_0/N_{\lvert l\rvert}$ gap (`R2-B6`); missing title, DOI (`R2-B1`). |
| 18 | `duffin1952class` | `L574–576` / `53, 138` | R. J. Duffin and A. C. Schaeffer, *"A class of nonharmonic Fourier series"*, *Trans. Am. Math. Soc.* **72**(2), 341--366 (1952), DOI `10.1090/S0002-9947-1952-0047179-6` | Core valid; missing title, end-page, DOI (`R2-B1`). |
| 19 | `ali1993continuous` | `L578–580` / `53, 138` | S. T. Ali, J.-P. Antoine, and J.-P. Gazeau, *"Continuous frames in Hilbert space"*, *Ann. Phys. (N.Y.)* **222**(1), 1--37 (1993), DOI `10.1006/aphy.1993.1016` | Core valid; missing title, end-page, DOI (`R2-B1`). |
| 20 | `christensen2003introduction` | `L582–584` / `53, 138` | O. Christensen, *An Introduction to Frames and Riesz Bases*, 1st ed. (Birkhäuser, Boston, 2003), DOI `10.1007/978-0-8176-8224-8` [2nd ed. 2016, DOI `10.1007/978-3-319-25613-9`] | Recommend 2nd ed. 2016 (`R2-B7`); missing DOI (`R2-B1`). |
| 21 | `gori1987bessel` | `L586–588` / `89` | F. Gori, G. Guattari, and C. Padovani, *"Bessel-Gauss beams"*, *Opt. Commun.* **64**(6), 491--495 (1987), DOI `10.1016/0030-4018(87)90276-8` | Core valid; missing title, end-page, DOI (`R2-B1`). |
| 22 | `gradshteyn2014table` | `L590–592` / `122, 420, 461` | I. S. Gradshteyn and I. M. Ryzhik, *Table of Integrals, Series, and Products*, 8th ed., edited by D. Zwillinger and V. Moll (Academic Press, Amsterdam/New York, 2014) | **CRITICAL (`R2-B4`):** `L461` cites wrong formula `6.643.2` $\to$ `6.631.1`; `L122, 420` omit `6.633.2`. |
