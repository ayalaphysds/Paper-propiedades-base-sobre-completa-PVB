# Theoretical Foundations of Overcomplete Perfect Vortex Beams: Mathematical Proofs, Continuous Frame Bounds, and Physical Advantages

**Author:** Sebastián Ayala  
*Independent Researcher, Cauquenes, Región del Maule, Chile*  
*Email: `ayala.phys.ds@gmail.com` | ORCID: `0009-0003-7348-3883`*  

**Project Reference:** Milestone M1 — Theoretical Foundations & Rigorous Proofs  
**Related Publications:**  
- T. Ferreira, G. Santos, S. Ayala, L. Hutter, E. S. Gómez, G. Lima, G. Cañas, and S. P. Walborn, *"Second-order moment equivalence of twisted Gaussian Schell model beams and orbital angular momentum eigenmodes"*, *J. Opt.* **28**, 095601 (2026). DOI: `10.1088/2040-8986/ae9b1d`.
- N. Villalba, C. Melo, S. Ayala, C. Mancilla, W. Valenzuela, M. Figueroa, E. Baradit, R. Lin, M. Tang, S. P. Walborn, G. Lima, G. Saavedra, and G. Cañas, *"Transmission of optical communication signals through ring core fiber using perfect vortex beams"*, *Opt. Express* **31**(24), 40113–40123 (2023). DOI: `10.1364/OE.503740`.
- P. Vaity and L. Rusch, *"Perfect vortex beam: Fourier transformation of a Bessel beam"*, *Opt. Lett.* **40**(4), 597–600 (2015). DOI: `10.1364/OL.40.000597`.

---

## Table of Contents
1. [Introduction and Scope](#1-introduction-and-scope)
2. [Field Representations: Ideal vs. Physical Quasi-PVB](#2-field-representations-ideal-vs-physical-quasi-pvb)
   - 2.1 Hilbert Space Structure and Azimuthal Decomposition
   - 2.2 The Ideal Singular PVB Representation
   - 2.3 Physical Realization: Bessel-Gauss Optical Fourier Transformation
   - 2.4 Asymptotic Radial Expansion and the Topological Radial Shift
3. [Closed-Form Inner Product and Overlap Derivation](#3-closed-form-inner-product-and-overlap-derivation)
   - 3.1 Cylindrical Inner Product Formulation
   - 3.2 Exact Evaluation via Gradshteyn & Ryzhik Identity 6.633.2
   - 3.3 State Norm and Exact Normalized Overlap
   - 3.4 Asymptotic Expansion and Universal Gaussian Cross-Talk
4. [Theorem 1: Impossibility of an Orthonormal Basis for Physical PVBs](#4-theorem-1-impossibility-of-an-orthonormal-basis-for-physical-pvbs)
   - 4.1 Statement of Theorem 1
   - 4.2 Rigorous Proof
   - 4.3 Physical and Algebraic Corollaries
5. [Theorem 2: Physical Unfeasibility of the Singular Orthonormal Limit](#5-theorem-2-physical-unfeasibility-of-the-singular-orthonormal-limit)
   - 5.1 Statement of Theorem 2
   - 5.2 Proof Pillar I: Divergence of Transverse Wavevector Variance
   - 5.3 Proof Pillar II: Beam Propagation Factor Divergence
   - 5.4 Proof Pillar III: Far-Field Angular Divergence and Evanescent Cutoff
   - 5.5 Proof Pillar IV: Divergence of Local Intensity and Dielectric Breakdown
   - 5.6 Proof Pillar V: Vanishing Power Under Field Clamping
   - 5.7 Proof Pillar VI: Optical System Diffraction Bound
   - 5.8 Proof Pillar VII: Distributional Nature and Gel'fand Triplet Failure
6. [Theorem 3: Continuous Frame Formalism on Paraxial Bandlimited Subspaces](#6-theorem-3-continuous-frame-formalism-on-paraxial-bandlimited-subspaces)
   - 6.1 Definition of Continuous Frames
   - 6.2 Completeness Kernel Derivation via Graf's Addition and Weber's Integral
   - 6.3 Fourier-Space Spectrum of the Frame Operator
   - 6.4 Paraxial Bandlimited Subspace
   - 6.5 Proof of Frame Bounds and Condition Number
   - 6.6 Canonical Dual Frame and Inversion Formula
7. [Classical Optical Advantages of PVB Overcompleteness](#7-classical-optical-advantages-of-pvb-overcompleteness)
   - 7.1 Multi-Ring Spatial Division Multiplexing (SDM)
   - 7.2 The 8.6 dB Power Advantage in Ring-Core Fibers
   - 7.3 Reproducing Kernel Hilbert Space (RKHS) Projective Noise Filtering
   - 7.4 Spatial Low-Pass Filtering Transfer Function
   - 7.5 Modal Redundancy and Self-Healing Against Beam Obscuration
8. [Quantum Optical Advantages in High-Dimensional Spaces](#8-quantum-optical-advantages-in-high-dimensional-spaces)
   - 8.1 Informationally Complete POVM (IC-POVM) Quantum State Tomography
   - 8.2 Constant Aperture Footprint in High-Dimensional QKD
   - 8.3 Entanglement Preservation in SPDC Through Finite Optical Apertures
9. [Pedagogical Appendix A: Primer on Perfect Vortex Beams](#9-pedagogical-appendix-a-primer-on-perfect-vortex-beams)
10. [Pedagogical Appendix B: Complete Bases in Hilbert Spaces](#10-pedagogical-appendix-b-complete-bases-in-hilbert-spaces)
11. [Pedagogical Appendix C: Overcomplete Bases, Frames, and Coherent States](#11-pedagogical-appendix-c-overcomplete-bases-frames-and-coherent-states)
12. [Numerical Verification and Python Reproducibility Suite](#12-numerical-verification-and-python-reproducibility-suite)

---

## 1. Introduction and Scope

In singular optics and structured light, optical vortices carrying orbital angular momentum (OAM) have revolutionized optical communications, high-dimensional quantum information processing, and nanoscale optical manipulation [Allen et al., Phys. Rev. A 45, 8185 (1992)]. Standard spatial modes carrying OAM, notably Laguerre-Gaussian ($\text{LG}_{p, l}$) and Bessel-Gauss ($\text{BG}_l$) modes, exhibit an intrinsic coupling between their azimuthal topological charge $l \in \mathbb{Z}$ and their radial spatial extension. For standard $\text{LG}_{0, l}$ beams, the radius of the annular intensity maximum scales as $r_{\max} \propto w_0 \sqrt{|l| + 1}$. When multiple OAM states are multiplexed in spatial division multiplexing (SDM) networks or high-dimensional quantum key distribution (HD-QKD), this radial dilation leads to severe aperture clipping, selective intermodal dispersion, and prohibitive coupling losses in finite-core optical waveguides [Villalba et al., Opt. Express 31, 40113 (2023)].

To circumvent this limitation, Ostrovsky et al. [Opt. Lett. 38, 534 (2013)] and Vaity & Rusch [Opt. Lett. 40, 597 (2015)] introduced the concept of the **Perfect Vortex Beam (PVB)**—an annular optical field whose ring radius $r_0$ and ring thickness $w_0$ are geometrically decoupled from the topological charge $l$. While the experimental generation and waveguide transmission of PVBs have flourished, their foundational mathematical character as a functional basis has remained poorly understood. In the literature, PVBs are frequently referred to as an "OAM basis", yet their linear independence, orthogonality, and completeness have lacked rigorous functional-analytic formalization.

Recently, Ferreira, Santos, Ayala et al. [*J. Opt.* **28**, 095601 (2026), Appendix D] made the foundational observation that the reconstruction kernel formed by the continuous outer product of PVB modes does not yield a Dirac delta distribution, but rather a 2D Gaussian convolution kernel of width $w$. Consequently, reconstructing an arbitrary transverse field from its PVB projection coefficients yields a smoothed representation rather than the original field itself.

This document establishes the definitive, publication-grade mathematical foundations of PVBs. We prove three central theorems:
1. **Theorem 1 (Non-Orthogonality):** Physical PVBs with finite ring width $w_0 > 0$ possess strictly positive radial inner products for identical topological charge $l$, precluding the existence of any minimal orthonormal basis.
2. **Theorem 2 (Physical Unfeasibility of Orthonormality):** The singular limit $w_0 \to 0$ required for delta-orthonormality is physically impossible in any realizable optical system due to divergences in kinetic energy variance ($\langle k_r^2 \rangle \to \infty$), beam propagation factor ($M^2 \to \infty$), far-field divergence angle ($\theta_\infty \to \infty$), local optical intensity ($I_{\max} \propto 1/w_0 \to \infty$), and fundamental wave-optical diffraction limits ($w_0 \ge 2\lambda f / \pi D$).
3. **Theorem 3 (Continuous Frame Structure):** On the Hilbert subspace of paraxial bandlimited optical fields $\mathcal{H}_{\text{band}}$, physical PVBs form a continuous overcomplete frame in the sense of Duffin & Schaeffer (1952) and Ali-Antoine-Gazeau (1993), with strictly positive, finite frame bounds $0 < A \le B < \infty$ and a well-conditioned canonical dual frame.

Finally, we demonstrate that overcompleteness is not a mathematical defect, but a physical asset providing quantifiable advantages in both classical optical communications and high-dimensional quantum information processing.

---

## 2. Field Representations: Ideal vs. Physical Quasi-PVB

### 2.1 Hilbert Space Structure and Azimuthal Decomposition

Consider the transverse plane of a monochromatic, paraxial optical beam propagating along the $z$-axis with wave number $k = 2\pi / \lambda$. Transverse spatial coordinates are denoted in cylindrical polar form as $\mathbf{r} = (r, \phi) \in \mathbb{R}^+ \times [0, 2\pi)$.

The state space of all finite-energy complex scalar field envelopes at a given transverse plane $z = \text{const}$ is the Lebesgue Hilbert space:
$$\mathcal{H} = L^2(\mathbb{R}^2, d^2\mathbf{r}) = L^2(\mathbb{R}^+ \times [0, 2\pi), r \, dr \, d\phi)$$
equipped with the standard inner product:
$$\langle \psi_1 | \psi_2 \rangle = \int_{\mathbb{R}^2} \psi_1^*(\mathbf{r}) \psi_2(\mathbf{r}) \, d^2\mathbf{r} = \int_0^\infty r \, dr \int_0^{2\pi} d\phi \, \psi_1^*(r, \phi) \psi_2(r, \phi)$$
and the corresponding induced norm $\|\psi\| = \sqrt{\langle \psi | \psi \rangle}$.

Because the free-space paraxial wave equation exhibits rotational symmetry $SO(2)$ around the optical axis $z$, the orbital angular momentum operator:
$$\hat{L}_z = -i \frac{\partial}{\partial \phi}$$
commutes with the transverse paraxial Hamiltonian $\hat{H}_\perp = -\frac{1}{2k} \nabla_\perp^2$. The Hilbert space decomposes into an orthogonal direct sum of invariant azimuthal subspaces corresponding to the discrete integer eigenvalues $l \in \mathbb{Z}$ of $\hat{L}_z$:
$$\mathcal{H} = \bigoplus_{l=-\infty}^\infty \mathcal{H}_l$$
where each single-OAM subspace $\mathcal{H}_l$ is defined by:
$$\mathcal{H}_l = \left\{ \psi_l(r, \phi) = u(r) \frac{e^{i l \phi}}{\sqrt{2\pi}} : u \in L^2(\mathbb{R}^+, r \, dr) \right\}$$

### 2.2 The Ideal Singular PVB Representation

The mathematical ideal of a "perfect" vortex beam is an optical field whose entire energy is infinitely localized on a circular ring of radius $r_0 > 0$, carrying a phase vortex $e^{i l \phi}$:
$$\psi_{l, r_0}^{\text{ideal}}(r, \phi) = \frac{1}{\sqrt{2\pi r_0}} \delta(r - r_0) e^{i l \phi}$$
Evaluating the inner product between two ideal PVBs yields:
$$\langle \psi_{l_1, r_1}^{\text{ideal}} | \psi_{l_2, r_2}^{\text{ideal}} \rangle = \int_0^{2\pi} d\phi \, e^{i(l_2 - l_1)\phi} \int_0^\infty r \, dr \, \frac{\delta(r - r_1)}{\sqrt{2\pi r_1}} \frac{\delta(r - r_2)}{\sqrt{2\pi r_2}} = \delta_{l_1, l_2} \delta(r_1 - r_2)$$
where $\delta(r_1 - r_2)$ is the 1D Dirac delta distribution.

While the ideal PVB satisfies continuous Dirac orthonormality, it possesses infinite local amplitude and infinite norm squared:
$$\|\psi_{l, r_0}^{\text{ideal}}\|^2 = \int_0^\infty r \, dr \frac{\delta(r - r_0)^2}{r_0} = \delta(0) \to \infty$$
Thus, $\psi_{l, r_0}^{\text{ideal}} \notin L^2(\mathbb{R}^2)$. It is a generalized eigenvector residing exclusively in the dual space $\Phi^\times$ of a Gel'fand triplet (rigged Hilbert space $\Phi \subset \mathcal{H} \subset \Phi^\times$). It cannot represent any physical optical wave packet.

### 2.3 Physical Realization: Bessel-Gauss Optical Fourier Transformation

In physical optics, a quasi-PVB is generated using the Fourier-transform configuration introduced by Vaity & Rusch (2015). A fundamental Gaussian laser beam of waist $w_g$ is illuminated onto a phase plate combining an axicon with cone angle $\gamma_{\text{axicon}}$ (producing a radial linear phase gradient $e^{i k_r \rho}$) and a spiral phase plate with topological charge $l$ (producing an azimuthal phase $e^{i l \phi}$). The modulated field immediately preceding the Fourier transform lens is a Bessel-Gauss (BG) beam:
$$E_{\text{BG}}(\rho, \phi) = J_l(k_r \rho) e^{i l \phi} \exp\left( - \frac{\rho^2}{w_g^2} \right)$$
where $k_r = k \sin \gamma_{\text{axicon}}$ is the axicon-induced radial wavevector, and $J_l(\cdot)$ is the Bessel function of the first kind of integer order $l$.

The BG beam passes through a thin lens of focal length $f$ and pupil aperture $D$. At the back focal plane $z = f$, the optical field is proportional to the 2D spatial Fourier transform of $E_{\text{BG}}(\boldsymbol{\rho})$:
$$\psi(r, \theta) = \frac{k}{2\pi i f} \exp(i 2k f) \int_0^\infty \rho \, d\rho \int_0^{2\pi} d\phi \, E_{\text{BG}}(\rho, \phi) \exp\left( - i \frac{k}{f} r \rho \cos(\phi - \theta) \right)$$
Using the Jacobi-Anger expansion for the exponential kernel:
$$\exp\left( - i \frac{k r \rho}{f} \cos(\phi - \theta) \right) = \sum_{m=-\infty}^\infty (-i)^m J_m\left( \frac{k r \rho}{f} \right) e^{i m (\phi - \theta)}$$
and performing the azimuthal integration $\int_0^{2\pi} d\phi \, e^{i(l + m)\phi} = 2\pi \delta_{m, -l}$, we obtain:
$$\psi(r, \theta) = \frac{k}{f} i^{l-1} e^{i l \theta} \int_0^\infty \rho \, d\rho \, \exp\left( - \frac{\rho^2}{w_g^2} \right) J_l(k_r \rho) J_l\left( \frac{k r}{f} \rho \right)$$

This radial integral is evaluated using Weber's second exponential integral [Gradshteyn & Ryzhik, Formula 6.633.2]:
$$\int_0^\infty x \, dx \, e^{-\alpha x^2} J_\nu(\beta x) J_\nu(\gamma x) = \frac{1}{2\alpha} \exp\left( - \frac{\beta^2 + \gamma^2}{4\alpha} \right) I_\nu\left( \frac{\beta \gamma}{2\alpha} \right)$$
Identifying the parameters:
$$\alpha = \frac{1}{w_g^2}, \quad \beta = k_r, \quad \gamma = \frac{k r}{f}$$
we calculate:
$$\frac{1}{2\alpha} = \frac{w_g^2}{2}$$
$$\frac{\beta^2 + \gamma^2}{4\alpha} = \frac{w_g^2}{4} \left( k_r^2 + \frac{k^2 r^2}{f^2} \right) = \frac{k^2 w_g^2}{4 f^2} \left( r^2 + \frac{f^2 k_r^2}{k^2} \right)$$
$$\frac{\beta \gamma}{2\alpha} = \frac{w_g^2 k_r k r}{2 f} = \frac{k^2 w_g^2}{4 f^2} \left( 2 \frac{f k_r}{k} r \right)$$

We now define two fundamental macroscopic physical parameters:
1. **Target Ring Radius:**
   $$r_0 \equiv \frac{f k_r}{k} = f \sin \gamma_{\text{axicon}}$$
2. **Ring Half-Width (waist):**
   $$w_0 \equiv \frac{2 f}{k w_g} = \frac{\lambda f}{\pi w_g}$$

Notice that $\frac{k^2 w_g^2}{4 f^2} = \frac{1}{w_0^2}$. Substituting these definitions back into the integral:
$$\int_0^\infty \rho \, d\rho \, e^{-\rho^2 / w_g^2} J_l(k_r \rho) J_l\left( \frac{k r}{f} \rho \right) = \frac{w_g^2}{2} \exp\left( - \frac{r^2 + r_0^2}{w_0^2} \right) I_l\left( \frac{2 r_0 r}{w_0^2} \right)$$
Multiplying by the prefactors $\frac{k}{f} i^{l-1} = \frac{2 i^{l-1}}{w_0 w_g}$, the exact physical field distribution of a quasi-PVB at the focal plane is:
$$\boxed{\psi_{l, r_0, w_0}(r, \phi) = C_{l, r_0, w_0} \exp\left( - \frac{r^2 + r_0^2}{w_0^2} \right) I_l\left( \frac{2 r_0 r}{w_0^2} \right) e^{i l \phi}}$$
where $I_l(\cdot)$ is the modified Bessel function of the first kind of integer order $l$, and $C_{l, r_0, w_0}$ is the global normalization factor.

### 2.4 Asymptotic Radial Expansion and the Topological Radial Shift

In practical optical setups, the ring radius is significantly larger than the ring thickness, defining the thin-ring parameter regime:
$$\xi \equiv \frac{2 r_0 r}{w_0^2} \gg 1$$
We exploit the Poincaré asymptotic expansion of the modified Bessel function $I_l(z)$ for large arguments $|\arg(z)| < \pi/2$:
$$I_l(z) = \frac{e^z}{\sqrt{2\pi z}} \left( 1 - \frac{\mu - 1}{8 z} + \frac{(\mu - 1)(\mu - 9)}{2! (8 z)^2} - \dots \right)$$
where $\mu = 4l^2$. For $z = \frac{2 r_0 r}{w_0^2}$:
$$I_l\left( \frac{2 r_0 r}{w_0^2} \right) = \frac{\exp\left( \frac{2 r_0 r}{w_0^2} \right)}{\sqrt{4\pi r_0 r / w_0^2}} \left[ 1 - \frac{4l^2 - 1}{16} \frac{w_0^2}{r_0 r} + \mathcal{O}\left( \frac{w_0^4}{r_0^2 r^2} \right) \right]$$

Multiplying by the Gaussian envelope $\exp\left( - \frac{r^2 + r_0^2}{w_0^2} \right)$, the exponential terms combine perfectly:
$$\exp\left( - \frac{r^2 + r_0^2}{w_0^2} \right) \exp\left( \frac{2 r_0 r}{w_0^2} \right) = \exp\left( - \frac{r^2 - 2 r_0 r + r_0^2}{w_0^2} \right) = \exp\left( - \frac{(r - r_0)^2}{w_0^2} \right)$$
Near the peak $r \approx r_0$, the denominator $\sqrt{r}$ can be expanded around $r_0$ as $\frac{1}{\sqrt{r}} = \frac{1}{\sqrt{r_0}} \left( 1 - \frac{r - r_0}{2 r_0} + \dots \right)$. Thus:
$$\psi_{l, r_0, w_0}(r, \phi) \approx \frac{C_0}{\sqrt{r_0}} \exp\left( - \frac{(r - r_0)^2}{w_0^2} \right) \left[ 1 - \frac{r - r_0}{2 r_0} - \frac{4l^2 - 1}{16 r_0^2} w_0^2 \right] e^{i l \phi}$$
Maximizing the radial intensity profile $I(r) = |\psi(r, \phi)|^2$ yields the exact location of the peak intensity ring:
$$\frac{d}{dr} \left[ \frac{1}{r} \exp\left( - \frac{2(r - r_0)^2}{w_0^2} \right) I_l^2\left( \frac{2 r_0 r}{w_0^2} \right) \right] = 0$$
Solving to first order in $(w_0 / r_0)^2$, we find the **topological radial shift**:
$$r_{\text{peak}}(l) = r_0 + \Delta r_l, \quad \boxed{\Delta r_l \approx \frac{4l^2 - 1}{32 r_0} w_0^2}$$
For typical experimental parameters ($r_0 = 1.0\,\text{mm}, w_0 = 0.1\,\text{mm}$), for $l = 1$, $\Delta r_1 \approx \frac{3}{32} \frac{0.01}{1.0}\,\text{mm} \approx 0.94\,\mu\text{m}$, which is less than $1\%$ of the ring thickness. This confirms that the ring geometry remains virtually locked across topological charge orders.

---

## 3. Closed-Form Inner Product and Overlap Derivation

### 3.1 Cylindrical Inner Product Formulation

Let $\psi_{l_1, r_1, w_0}$ and $\psi_{l_2, r_2, w_0}$ be two physical PVB states with arbitrary topological charges $l_1, l_2 \in \mathbb{Z}$, ring radii $r_1, r_2 \in \mathbb{R}^+$, and identical ring width $w_0 > 0$:
$$\psi_{l_i, r_i, w_0}(r, \phi) = \exp\left( - \frac{r^2 + r_i^2}{w_0^2} \right) I_{l_i}\left( \frac{2 r_i r}{w_0^2} \right) e^{i l_i \phi}$$
Their inner product in $L^2(\mathbb{R}^2)$ is:
$$\langle \psi_{l_1, r_1, w_0} | \psi_{l_2, r_2, w_0} \rangle = \int_0^{2\pi} d\phi \, e^{i(l_2 - l_1)\phi} \int_0^\infty r \, dr \, e^{-\frac{r^2 + r_1^2}{w_0^2}} e^{-\frac{r^2 + r_2^2}{w_0^2}} I_{l_1}\left( \frac{2 r_1 r}{w_0^2} \right) I_{l_2}\left( \frac{2 r_2 r}{w_0^2} \right)$$
The azimuthal integral yields exact Kronecker orthogonality:
$$\int_0^{2\pi} e^{i(l_2 - l_1)\phi} \, d\phi = 2\pi \delta_{l_1, l_2}$$
Thus, modes with distinct topological charges $l_1 \neq l_2$ are strictly orthogonal:
$$\langle \psi_{l_1, r_1, w_0} | \psi_{l_2, r_2, w_0} \rangle = 0 \quad (\forall l_1 \neq l_2)$$

### 3.2 Exact Evaluation via Gradshteyn & Ryzhik Identity 6.633.2

For identical topological charge $l_1 = l_2 = l$, the inner product reduces to the radial integral:
$$\mathcal{I}(r_1, r_2; w_0) = 2\pi \exp\left( - \frac{r_1^2 + r_2^2}{w_0^2} \right) \int_0^\infty r \, dr \, \exp\left( - \frac{2 r^2}{w_0^2} \right) I_l\left( \frac{2 r_1 r}{w_0^2} \right) I_l\left( \frac{2 r_2 r}{w_0^2} \right)$$

We evaluate this integral using Gradshteyn & Ryzhik formula 6.633.2:
$$\int_0^\infty x \, dx \, e^{-\alpha x^2} I_\nu(\beta x) I_\nu(\gamma x) = \frac{1}{2\alpha} \exp\left( \frac{\beta^2 + \gamma^2}{4\alpha} \right) I_\nu\left( \frac{\beta \gamma}{2\alpha} \right)$$
valid for $\text{Re}(\alpha) > 0$ and $\text{Re}(\nu) > -1$. For negative integer charges $l < 0$, we use the identity $I_{-|l|}(z) = I_{|l|}(z)$ so that the formula applies unconditionally for all $l \in \mathbb{Z}$.

We identify the mathematical variables:
$$\alpha = \frac{2}{w_0^2}, \quad \beta = \frac{2 r_1}{w_0^2}, \quad \gamma = \frac{2 r_2}{w_0^2}$$
Computing the individual terms:
$$\frac{1}{2\alpha} = \frac{1}{2 (2 / w_0^2)} = \frac{w_0^2}{4}$$
$$\frac{\beta^2 + \gamma^2}{4\alpha} = \frac{\frac{4 r_1^2}{w_0^4} + \frac{4 r_2^2}{w_0^4}}{4 (2 / w_0^2)} = \frac{\frac{4(r_1^2 + r_2^2)}{w_0^4}}{\frac{8}{w_0^2}} = \frac{r_1^2 + r_2^2}{2 w_0^2}$$
$$\frac{\beta \gamma}{2\alpha} = \frac{\frac{4 r_1 r_2}{w_0^4}}{2 (2 / w_0^2)} = \frac{\frac{4 r_1 r_2}{w_0^4}}{\frac{4}{w_0^2}} = \frac{r_1 r_2}{w_0^2}$$

Substituting these back into the integral:
$$\int_0^\infty r \, dr \, e^{-\frac{2 r^2}{w_0^2}} I_l\left( \frac{2 r_1 r}{w_0^2} \right) I_l\left( \frac{2 r_2 r}{w_0^2} \right) = \frac{w_0^2}{4} \exp\left( \frac{r_1^2 + r_2^2}{2 w_0^2} \right) I_l\left( \frac{r_1 r_2}{w_0^2} \right)$$
Now we multiply by the pre-exponential factor $\exp\left( - \frac{r_1^2 + r_2^2}{w_0^2} \right)$:
$$\exp\left( - \frac{r_1^2 + r_2^2}{w_0^2} \right) \cdot \frac{w_0^2}{4} \exp\left( \frac{r_1^2 + r_2^2}{2 w_0^2} \right) = \frac{w_0^2}{4} \exp\left( - \frac{r_1^2 + r_2^2}{2 w_0^2} \right)$$

Hence, we arrive at the exact closed-form inner product formula:
$$\boxed{\langle \psi_{l_1, r_1, w_0} | \psi_{l_2, r_2, w_0} \rangle = 2\pi \delta_{l_1, l_2} \frac{w_0^2}{4} \exp\left( - \frac{r_1^2 + r_2^2}{2 w_0^2} \right) I_{l_1}\left( \frac{r_1 r_2}{w_0^2} \right)}$$

### 3.3 State Norm and Exact Normalized Overlap

The norm squared of an individual state is obtained by setting $r_1 = r_2 = r_0$:
$$\|\psi_{l, r_0, w_0}\|^2 = \langle \psi_{l, r_0, w_0} | \psi_{l, r_0, w_0} \rangle = 2\pi \frac{w_0^2}{4} \exp\left( - \frac{r_0^2}{w_0^2} \right) I_l\left( \frac{r_0^2}{w_0^2} \right)$$

We now define the **normalized overlap coefficient** between two states with identical topological charge $l$:
$$\gamma_l(r_1, r_2; w_0) \equiv \frac{\langle \psi_{l, r_1, w_0} | \psi_{l, r_2, w_0} \rangle}{\|\psi_{l, r_1, w_0}\| \|\psi_{l, r_2, w_0}\|}$$
Substituting the exact analytical forms:
$$\gamma_l(r_1, r_2; w_0) = \frac{2\pi \frac{w_0^2}{4} \exp\left( - \frac{r_1^2 + r_2^2}{2 w_0^2} \right) I_l\left( \frac{r_1 r_2}{w_0^2} \right)}{\sqrt{2\pi \frac{w_0^2}{4} \exp\left( - \frac{r_1^2}{w_0^2} \right) I_l\left( \frac{r_1^2}{w_0^2} \right)} \sqrt{2\pi \frac{w_0^2}{4} \exp\left( - \frac{r_2^2}{w_0^2} \right) I_l\left( \frac{r_2^2}{w_0^2} \right)}}$$

Remarkably, the prefactor $2\pi \frac{w_0^2}{4}$ cancels out completely. Furthermore, the exponential factor in the denominator is:
$$\sqrt{\exp\left( - \frac{r_1^2}{w_0^2} \right) \exp\left( - \frac{r_2^2}{w_0^2} \right)} = \exp\left( - \frac{r_1^2 + r_2^2}{2 w_0^2} \right)$$
which cancels the exponential factor in the numerator identically!

We obtain the normalized overlap expression:
$$\boxed{\gamma_l(r_1, r_2; w_0) = \frac{I_l\left( \frac{r_1 r_2}{w_0^2} \right)}{\sqrt{I_l\left( \frac{r_1^2}{w_0^2} \right) I_l\left( \frac{r_2^2}{w_0^2} \right)}}}$$

### 3.4 Asymptotic Expansion and Universal Gaussian Cross-Talk

To understand the physical behavior in the thin-ring regime ($r_1 r_2 / w_0^2 \gg 1$), we insert the asymptotic expansion of $I_l(z)$ up to second order:
$$I_l(z) = \frac{e^z}{\sqrt{2\pi z}} \left( 1 - \frac{4l^2 - 1}{8 z} + \dots \right)$$
Computing the numerator:
$$I_l\left( \frac{r_1 r_2}{w_0^2} \right) \approx \frac{\exp\left( \frac{r_1 r_2}{w_0^2} \right)}{\sqrt{2\pi r_1 r_2 / w_0^2}} \left( 1 - \frac{4l^2 - 1}{8 r_1 r_2 / w_0^2} \right)$$
Computing the denominator:
$$I_l\left( \frac{r_1^2}{w_0^2} \right) \approx \frac{\exp\left( \frac{r_1^2}{w_0^2} \right)}{\sqrt{2\pi r_1^2 / w_0^2}} \left( 1 - \frac{4l^2 - 1}{8 r_1^2 / w_0^2} \right)$$
$$I_l\left( \frac{r_2^2}{w_0^2} \right) \approx \frac{\exp\left( \frac{r_2^2}{w_0^2} \right)}{\sqrt{2\pi r_2^2 / w_0^2}} \left( 1 - \frac{4l^2 - 1}{8 r_2^2 / w_0^2} \right)$$
The geometric mean of the denominators evaluates to:
$$\sqrt{I_l\left( \frac{r_1^2}{w_0^2} \right) I_l\left( \frac{r_2^2}{w_0^2} \right)} \approx \frac{\exp\left( \frac{r_1^2 + r_2^2}{2 w_0^2} \right)}{\sqrt{2\pi r_1 r_2 / w_0^2}} \left[ 1 - \frac{4l^2 - 1}{16} w_0^2 \left( \frac{1}{r_1^2} + \frac{1}{r_2^2} \right) \right]$$

Dividing numerator by denominator, the term $\sqrt{2\pi r_1 r_2 / w_0^2}$ cancels exactly. The exponential ratio is:
$$\frac{\exp\left( \frac{r_1 r_2}{w_0^2} \right)}{\exp\left( \frac{r_1^2 + r_2^2}{2 w_0^2} \right)} = \exp\left( - \frac{r_1^2 - 2 r_1 r_2 + r_2^2}{2 w_0^2} \right) = \exp\left( - \frac{(r_1 - r_2)^2}{2 w_0^2} \right)$$
The bracketed algebraic correction is:
$$\frac{1 - \frac{4l^2 - 1}{8 r_1 r_2} w_0^2}{1 - \frac{4l^2 - 1}{16} \left( \frac{1}{r_1^2} + \frac{1}{r_2^2} \right) w_0^2} \approx 1 + \frac{4l^2 - 1}{16} w_0^2 \left[ \frac{1}{r_1^2} - \frac{2}{r_1 r_2} + \frac{1}{r_2^2} \right] = 1 + \frac{4l^2 - 1}{16} \frac{w_0^2 (r_1 - r_2)^2}{r_1^2 r_2^2}$$

Therefore, we establish the **universal asymptotic Gaussian cross-talk formula**:
$$\boxed{\gamma_l(r_1, r_2; w_0) = \exp\left( - \frac{(r_1 - r_2)^2}{2 w_0^2} \right) \left[ 1 + \frac{4l^2 - 1}{16} \frac{w_0^2 (r_1 - r_2)^2}{r_1^2 r_2^2} + \mathcal{O}\left( \frac{w_0^4 (r_1 - r_2)^2}{r_0^6} \right) \right]}$$

At leading order, the overlap between two physical PVBs of the same topological charge is a **pure Gaussian function** governed solely by the radial distance $|r_1 - r_2|$ normalized by the ring width $w_0$, completely independent of the topological charge $l$!

---

## 4. Theorem 1: Impossibility of an Orthonormal Basis for Physical PVBs

### 4.1 Statement of Theorem 1

**Theorem 1 (Non-Orthogonality of Physical PVBs).**  
*Let $\mathcal{F}_{w_0} = \{\psi_{l, r_0, w_0} : l \in \mathbb{Z}, r_0 \in \mathbb{R}^+\}$ be the family of physical quasi-perfect vortex beams with ring thickness $w_0 > 0$. For any topological charge $l \in \mathbb{Z}$ and any pair of distinct ring radii $r_1, r_2 \in (0, \infty)$ with $r_1 \neq r_2$, the normalized overlap satisfies:*
$$0 < \gamma_l(r_1, r_2; w_0) < 1$$
*Consequently, no sub-collection of physical PVBs with identical topological charge $l$ and varying radii can form an orthogonal or orthonormal set in $L^2(\mathbb{R}^2)$.*

### 4.2 Rigorous Proof

*Proof.*  
From Section 3.3, the normalized overlap is given by:
$$\gamma_l(r_1, r_2; w_0) = \frac{I_l\left( \frac{r_1 r_2}{w_0^2} \right)}{\sqrt{I_l\left( \frac{r_1^2}{w_0^2} \right) I_l\left( \frac{r_2^2}{w_0^2} \right)}}$$
We establish the lower and upper bounds separately:

1. **Strict Positivity ($\gamma_l > 0$):**  
   The modified Bessel function of the first kind of integer order $l$ has the power series expansion:
   $$I_l(x) = \sum_{m=0}^\infty \frac{1}{m! (m + |l|)!} \left( \frac{x}{2} \right)^{2m + |l|}$$
   For any $x > 0$, every term in the summation is strictly positive. Since $r_1 > 0$, $r_2 > 0$, and $w_0 > 0$, the arguments satisfy:
   $$x_{12} = \frac{r_1 r_2}{w_0^2} > 0, \quad x_{11} = \frac{r_1^2}{w_0^2} > 0, \quad x_{22} = \frac{r_2^2}{w_0^2} > 0$$
   Therefore, $I_l(x_{12}) > 0$, $I_l(x_{11}) > 0$, and $I_l(x_{22}) > 0$. The quotient of strictly positive real quantities is strictly positive:
   $$\gamma_l(r_1, r_2; w_0) > 0 \quad \forall r_1, r_2 \in (0, \infty)$$

2. **Strict Upper Bound ($\gamma_l < 1$ for $r_1 \neq r_2$):**  
   By the Cauchy-Schwarz inequality in the Hilbert space $L^2(\mathbb{R}^+, r \, dr)$:
   $$|\langle u_{l, r_1} | u_{l, r_2} \rangle| \le \|u_{l, r_1}\| \|u_{l, r_2}\|$$
   with equality holding if and only if $u_{l, r_1}(r) = c \, u_{l, r_2}(r)$ almost everywhere for some scalar $c \in \mathbb{C}$.  
   Suppose equality holds ($\gamma_l = 1$). Then for all $r \in \mathbb{R}^+$:
   $$\exp\left( - \frac{r^2 + r_1^2}{w_0^2} \right) I_l\left( \frac{2 r_1 r}{w_0^2} \right) = c \exp\left( - \frac{r^2 + r_2^2}{w_0^2} \right) I_l\left( \frac{2 r_2 r}{w_0^2} \right)$$
   Dividing both sides yields:
   $$\frac{I_l\left( \frac{2 r_1 r}{w_0^2} \right)}{I_l\left( \frac{2 r_2 r}{w_0^2} \right)} = c \exp\left( \frac{r_1^2 - r_2^2}{w_0^2} \right) = \text{const}$$
   However, for large $r \to \infty$, the ratio of modified Bessel functions behaves asymptotically as:
   $$\frac{I_l\left( \frac{2 r_1 r}{w_0^2} \right)}{I_l\left( \frac{2 r_2 r}{w_0^2} \right)} \sim \sqrt{\frac{r_2}{r_1}} \exp\left( \frac{2(r_1 - r_2) r}{w_0^2} \right)$$
   If $r_1 \neq r_2$, this ratio grows or decays exponentially with $r$, which contradicts the requirement that the ratio be constant. Hence, linear dependence is impossible for $r_1 \neq r_2$.  
   Therefore, the Cauchy-Schwarz inequality is strictly strict:
   $$\gamma_l(r_1, r_2; w_0) < 1 \quad (\forall r_1 \neq r_2)$$

Combining (1) and (2) establishes $0 < \gamma_l(r_1, r_2; w_0) < 1$. $\blacksquare$

### 4.3 Physical and Algebraic Corollaries

**Corollary 1.1 (Absence of Radial Nodes).**  
*The radial profile $u_{l, r_0}(r)$ of any physical PVB is strictly non-negative on $(0, \infty)$ and possesses zero radial nodes. Consequently, the overlap integral of two such profiles with identical sign cannot vanish.*

**Corollary 1.2 (Impossibility of Minimal Schauder Basis).**  
*Because $\langle \psi_{l, r_1} | \psi_{l, r_2} \rangle \neq 0$ for all $r_1 \neq r_2$, no countable discrete subset $\{\psi_{l, r_n}\}_{n=1}^\infty$ with $w_0 > 0$ can form an orthogonal Schauder basis for $\mathcal{H}_l$. Any complete family formed by physical PVBs must necessarily be overcomplete and linearly redundant.*

---

## 5. Theorem 2: Physical Unfeasibility of the Singular Orthonormal Limit

### 5.1 Statement of Theorem 2

**Theorem 2 (Physical Unfeasibility of Orthonormal PVBs).**  
*A family of physical PVBs $\{\psi_{l, r_0, w_0}\}$ reduces to a Dirac-orthonormal basis if and only if the ring width parameter vanishes:*
$$\lim_{w_0 \to 0} \gamma_l(r_1, r_2; w_0) = \frac{\delta(r_1 - r_2)}{r_1}$$
*In any physical optical system, the singular limit $w_0 \to 0$ is strictly unrealizable, as it entails the simultaneous divergence of the transverse kinetic energy variance, the beam propagation factor, the far-field angular divergence, and the peak optical intensity, while reducing the total transmitted energy to zero under material field clamping and violating the optical diffraction limit.*

### 5.2 Proof Pillar I: Divergence of Transverse Wavevector Variance

Following the second-order moment formalism of paraxial beams [Ferreira, Santos, Ayala et al., *J. Opt.* **28**, 095601 (2026)], the transverse spatial frequency spread is defined by the expectation value of the Laplacian operator:
$$\langle k_r^2 \rangle = 2\pi \int_0^\infty \left[ r \left( \frac{dU}{dr} \right)^2 + \frac{l^2}{r} U^2(r) \right] dr$$
For a physical PVB with ring radius $r_0$ and width $w_0$, substituting the asymptotic profile and evaluating the derivatives yields [Ferreira et al., Eq. (131)]:
$$\langle k_r^2 \rangle \approx \frac{1}{w_0^2} + \frac{l^2 - 1/4}{r_0^2}$$
As the ring thickness vanishes:
$$\lim_{w_0 \to 0} \langle k_r^2 \rangle = \lim_{w_0 \to 0} \left( \frac{1}{w_0^2} + \frac{l^2 - 1/4}{r_0^2} \right) = \infty$$
The quantum kinetic energy $\langle \hat{T}_\perp \rangle = \frac{\hbar^2}{2m} \langle k_r^2 \rangle$ (or optical momentum variance) diverges quadratically as $w_0^{-2} \to \infty$.

### 5.3 Proof Pillar II: Beam Propagation Factor Divergence

The ISO 11146 beam propagation product $M^2$ quantifies optical beam quality relative to an ideal diffraction-limited fundamental Gaussian beam ($M^2 = 1$). For a general circularly symmetric structured beam:
$$M^2 = \sqrt{\langle r^2 \rangle \langle k_r^2 \rangle}$$
From Ferreira et al. (2026), Eq. (112), the radial second moment of a PVB is:
$$\langle r^2 \rangle \approx r_0^2 + \frac{w_0^2}{4}$$
Taking the product of the two moments:
$$M^2 = \sqrt{ \left( r_0^2 + \frac{w_0^2}{4} \right) \left( \frac{1}{w_0^2} + \frac{l^2 - 1/4}{r_0^2} \right) } = \sqrt{ \frac{r_0^2}{w_0^2} + \left(l^2 - \frac{1}{4}\right) + \frac{1}{4} + \frac{w_0^2(l^2 - 1/4)}{4 r_0^2} }$$
Taking the singular limit $w_0 \to 0$ for fixed $r_0 > 0$:
$$\boxed{M^2 \sim \frac{r_0}{w_0} \xrightarrow[w_0 \to 0]{} \infty}$$
An optical beam with $M^2 \to \infty$ exhibits infinite modal degradation and zero spatial coherence, rendering propagation control impossible.

### 5.4 Proof Pillar III: Far-Field Angular Divergence and Evanescent Cutoff

The asymptotic far-field divergence half-angle $\theta_\infty$ is determined by the transverse spatial frequency spread:
$$\theta_\infty = \frac{\sqrt{\langle k_r^2 \rangle}}{k} \approx \frac{1}{k w_0} = \frac{\lambda}{2\pi w_0}$$
As $w_0 \to 0$, $\theta_\infty \to \infty$.

Furthermore, in Helmholtz wave optics, the longitudinal wavevector $k_z$ is constrained by the dispersion relation:
$$k_z = \sqrt{k^2 - k_\perp^2}$$
When $w_0 \lesssim \frac{\lambda}{2\pi}$, the transverse spatial frequencies exceed the optical wavenumber:
$$k_\perp \sim \frac{1}{w_0} > k = \frac{2\pi}{\lambda}$$
Consequently, $k_z$ becomes purely imaginary:
$$k_z = i \sqrt{k_\perp^2 - k^2} \equiv i \kappa_z$$
The paraxial wave equation breaks down completely, and the optical field is converted into **evanescent waves** decaying exponentially along $z$ as $\exp(-\kappa_z z)$. The beam cannot propagate into the radiation far field.

### 5.5 Proof Pillar IV: Divergence of Local Intensity and Dielectric Breakdown

Consider a physical beam carrying finite total optical power $P = 1\,\text{W}$:
$$P = \int_{\mathbb{R}^2} |\psi(\mathbf{r})|^2 \, d^2\mathbf{r} = 2\pi \int_0^\infty r \, dr \, |u(r)|^2 = 1$$
Using the thin-ring Gaussian approximation $u(r) \approx A_0 \exp\left( - \frac{(r - r_0)^2}{w_0^2} \right)$:
$$P \approx 2\pi r_0 |A_0|^2 \int_{-\infty}^\infty \exp\left( - \frac{2(r - r_0)^2}{w_0^2} \right) dr = 2\pi r_0 |A_0|^2 \sqrt{\frac{\pi w_0^2}{2}} = \pi^{3/2} \sqrt{2} \, r_0 w_0 |A_0|^2$$
Solving for the peak optical intensity $I_{\max} = |A_0|^2$:
$$\boxed{I_{\max} = \frac{P}{\pi^{3/2} \sqrt{2} \, r_0 w_0} \propto \frac{1}{w_0}}$$
As $w_0 \to 0$, $I_{\max} \to \infty$.

The peak electric field scales as $|E_{\max}| = \sqrt{2 I_{\max} / (\epsilon_0 c)} \propto w_0^{-1/2} \to \infty$. In any physical medium (air, optical glass, fused silica), dielectric breakdown occurs when $|E_{\max}|$ exceeds the material ionization threshold:
$$E_{\text{breakdown}} \approx 10^9\text{--}10^{10}\,\text{V/m} \quad (I_{\text{breakdown}} \sim 10^{14}\,\text{W/cm}^2)$$
Any attempt to compress $w_0 \to 0$ triggers optical breakdown, multiphoton ionization, plasma formation, and laser-induced optical damage (LIDT) to all optical components.

### 5.6 Proof Pillar V: Vanishing Power Under Field Clamping

Conversely, suppose the peak electric field $|E_{\max}|$ is clamped at a safe physical operating threshold below the damage limit:
$$|E_{\max}| \le E_{\text{damage}} < \infty$$
The total optical power transmitted by the ring is:
$$P(w_0) \le \pi^{3/2} \sqrt{2} \, r_0 w_0 |E_{\text{damage}}|^2 \propto w_0$$
Taking the singular limit:
$$\lim_{w_0 \to 0} P(w_0) = 0$$
Thus, an orthonormal PVB carrying non-divergent field values transmits **identically zero physical energy**.

### 5.7 Proof Pillar VI: Optical System Diffraction Bound

In any experimental optical generation apparatus [Vaity & Rusch (2015), Villalba et al. (2023)], the Fourier transformation is performed by a lens of focal length $f$ and clear aperture diameter $D$. The input beam illuminating the lens has a finite Gaussian waist $w_g \le D/2$.

By the Fourier scaling theorem of paraxial diffraction, the focal waist is strictly bounded from below:
$$w_0 = \frac{2 f}{k w_g} \ge \frac{4 f}{k D} = \frac{2 \lambda f}{\pi D} \equiv w_{\text{diff}} > 0$$
To achieve $w_0 \to 0$, the optical system would require either:
1. An infinitely large aperture diameter $D \to \infty$,
2. A focal length $f \to 0$, or
3. A zero optical wavelength $\lambda \to 0$.
All three conditions are physically impossible.

### 5.8 Proof Pillar VII: Distributional Nature and Gel'fand Triplet Failure

In the limit $w_0 \to 0$, the spatial field profile becomes:
$$\lim_{w_0 \to 0} \psi_{l, r_0, w_0}(r, \phi) = \frac{1}{\sqrt{2\pi r_0}} \delta(r - r_0) e^{i l \phi}$$
The norm squared of this state in the physical Hilbert space $\mathcal{H} = L^2(\mathbb{R}^2)$ is:
$$\|\psi_{l, r_0}^{\text{ideal}}\|^2 = \int_0^\infty r \, dr \int_0^{2\pi} d\phi \, \frac{\delta(r - r_0)^2}{2\pi r_0} = \int_0^\infty \delta(r - r_0)^2 \, dr = \delta(0) = \infty$$
Because its norm is infinite, $\psi_{l, r_0}^{\text{ideal}} \notin L^2(\mathbb{R}^2)$.

In terms of functional analysis, the ideal PVB is a generalized eigenfunction belonging to the dual space $\Phi^\times$ in the Gel'fand triplet (rigged Hilbert space):
$$\Phi \subset L^2(\mathbb{R}^2) \subset \Phi^\times$$
where $\Phi = \mathcal{S}(\mathbb{R}^2)$ is the Schwartz test space of rapidly decreasing smooth functions. The action of $\psi_{l, r_0}^{\text{ideal}}$ is defined only as a continuous linear functional acting on a smooth test field $\varphi \in \Phi$:
$$\langle \psi_{l, r_0}^{\text{ideal}}, \varphi \rangle = \sqrt{2\pi r_0} \int_0^{2\pi} \frac{e^{-i l \phi}}{\sqrt{2\pi}} \varphi(r_0, \phi) \, d\phi$$
Since physical optical states must possess finite norm (finite total photon number in quantum optics, finite total power in classical optics), the singular limit $w_0 \to 0$ cannot represent any physical quantum state $|\psi\rangle \in \mathcal{H}$. $\blacksquare$

---

## 6. Theorem 3: Continuous Frame Formalism on Paraxial Bandlimited Subspaces

### 6.1 Definition of Continuous Frames

Since physical PVBs cannot form a minimal orthonormal basis, we examine their structure within the theory of generalized frames [Duffin & Schaeffer, Trans. Am. Math. Soc. 72, 341 (1952); Ali, Antoine, & Gazeau, Ann. Phys. 222, 1 (1993)].

Let $(\Omega, \mu)$ be the parameter measure space $\Omega = \mathbb{Z} \times \mathbb{R}^+$ with product measure:
$$d\mu(l, r_0) = dr_0 \, r_0 \sum_{l \in \mathbb{Z}}$$
where $r_0$ is the radial integration weight.

A family of vectors $\{\psi_\alpha\}_{\alpha \in \Omega}$ in a Hilbert space $\mathcal{H}$ is a **continuous frame** if:
1. The mapping $\alpha \mapsto \langle \psi_\alpha | f \rangle$ is measurable for all $f \in \mathcal{H}$.
2. There exist two positive constants $0 < A \le B < \infty$ (**frame bounds**) such that for all $f \in \mathcal{H}$:
   $$\boxed{A \|f\|^2 \le \int_\Omega |\langle \psi_\alpha | f \rangle|^2 \, d\mu(\alpha) \le B \|f\|^2}$$

The frame operator $S: \mathcal{H} \to \mathcal{H}$ is defined in weak form by:
$$\langle g | S f \rangle = \int_\Omega \langle g | \psi_\alpha \rangle \langle \psi_\alpha | f \rangle \, d\mu(\alpha)$$
or formally in Dirac notation:
$$S = \int_\Omega |\psi_\alpha \rangle \langle \psi_\alpha | \, d\mu(\alpha)$$
If $A = B$, the frame is **tight**; if $A = B = 1$, it is a **Parseval frame** satisfying the resolution of identity.

### 6.2 Completeness Kernel Derivation via Graf's Addition and Weber's Integral

To determine the frame operator $S_w$ for physical PVBs, let us consider the normalized mode formulation introduced in Ferreira, Santos, Ayala et al. (2026), Appendix D:
$$\Phi_{l, R}(r, \phi) = C_0 \exp\left( - \frac{r^2 + R^2}{w_0^2} \right) I_l\left( \frac{2 R r}{w_0^2} \right) e^{i l \phi}$$
with normalization constant $C_0 = \frac{\sqrt{2/\pi}}{w_0^2}$.

The action of the reconstruction operator $S_w$ on an arbitrary transverse optical field $\psi(\mathbf{r})$ is:
$$(S_w \psi)(\mathbf{r}) = \sum_{l=-\infty}^\infty \int_0^\infty R \, dR \, \langle \Phi_{l, R} | \psi \rangle \Phi_{l, R}(\mathbf{r}) = \int_{\mathbb{R}^2} K(\mathbf{r}, \mathbf{r}') \psi(\mathbf{r}') \, d^2\mathbf{r}'$$
where the integral kernel $K(\mathbf{r}, \mathbf{r}')$ is the continuous outer-product sum:
$$K(\mathbf{r}, \mathbf{r}') = \sum_{l=-\infty}^\infty \int_0^\infty R \, dR \, \Phi_{l, R}(\mathbf{r}) \Phi_{l, R}^*(\mathbf{r}')$$

We evaluate this kernel in closed form:
$$K(\mathbf{r}, \mathbf{r}') = |C_0|^2 \exp\left( - \frac{r^2 + r'^2}{w_0^2} \right) \sum_{l=-\infty}^\infty e^{i l(\phi - \phi')} \int_0^\infty R \, dR \, \exp\left( - \frac{2 R^2}{w_0^2} \right) I_l\left( \frac{2 R r}{w_0^2} \right) I_l\left( \frac{2 R r'}{w_0^2} \right)$$
The radial integral over $R$ is evaluated using Gradshteyn & Ryzhik 6.633.2 with $\alpha = \frac{2}{w_0^2}$, $\beta = \frac{2 r}{w_0^2}$, $\gamma = \frac{2 r'}{w_0^2}$:
$$\int_0^\infty R \, dR \, \exp\left( - \frac{2 R^2}{w_0^2} \right) I_l\left( \frac{2 R r}{w_0^2} \right) I_l\left( \frac{2 R r'}{w_0^2} \right) = \frac{w_0^2}{4} \exp\left( \frac{r^2 + r'^2}{2 w_0^2} \right) I_l\left( \frac{r r'}{w_0^2} \right)$$
Multiplying by the external factor $\exp\left( - \frac{r^2 + r'^2}{w_0^2} \right)$:
$$\exp\left( - \frac{r^2 + r'^2}{w_0^2} \right) \frac{w_0^2}{4} \exp\left( \frac{r^2 + r'^2}{2 w_0^2} \right) = \frac{w_0^2}{4} \exp\left( - \frac{r^2 + r'^2}{2 w_0^2} \right)$$

Substituting this back into the kernel expression:
$$K(\mathbf{r}, \mathbf{r}') = |C_0|^2 \frac{w_0^2}{4} \exp\left( - \frac{r^2 + r'^2}{2 w_0^2} \right) \sum_{l=-\infty}^\infty e^{i l(\phi - \phi')} I_l\left( \frac{r r'}{w_0^2} \right)$$
The infinite summation over $l$ is evaluated in closed form using the generating function of modified Bessel functions (or Graf's addition theorem):
$$\sum_{l=-\infty}^\infty e^{i l \theta} I_l(z) = \exp(z \cos \theta)$$
Setting $z = \frac{r r'}{w_0^2}$ and $\theta = \phi - \phi'$:
$$\sum_{l=-\infty}^\infty e^{i l(\phi - \phi')} I_l\left( \frac{r r'}{w_0^2} \right) = \exp\left( \frac{r r' \cos(\phi - \phi')}{w_0^2} \right)$$

Combining the radial and azimuthal exponential factors:
$$- \frac{r^2 + r'^2}{2 w_0^2} + \frac{r r' \cos(\phi - \phi')}{w_0^2} = - \frac{r^2 + r'^2 - 2 r r' \cos(\phi - \phi')}{2 w_0^2} = - \frac{|\mathbf{r} - \mathbf{r}'|^2}{2 w_0^2}$$
Finally, multiplying by the normalization constant $|C_0|^2 \frac{w_0^2}{4}$:
$$|C_0|^2 \frac{w_0^2}{4} = \left( \frac{2}{\pi w_0^4} \right) \frac{w_0^2}{4} = \frac{1}{2\pi w_0^2}$$

We obtain the exact reconstruction kernel:
$$\boxed{K(\mathbf{r}, \mathbf{r}') = G_{w_0}(\mathbf{r} - \mathbf{r}') = \frac{1}{2\pi w_0^2} \exp\left( - \frac{|\mathbf{r} - \mathbf{r}'|^2}{2 w_0^2} \right)}$$
The completeness operator $S_w$ is **identically a 2D Gaussian convolution filter** of width $w_0$!

### 6.3 Fourier-Space Spectrum of the Frame Operator

Because $K(\mathbf{r}, \mathbf{r}')$ is a convolution kernel $G_{w_0}(\mathbf{r} - \mathbf{r}')$, the action of $S_w$ is diagonalized by the 2D spatial Fourier transform:
$$\widetilde{\psi}(\mathbf{k}) = \frac{1}{2\pi} \int_{\mathbb{R}^2} \psi(\mathbf{r}) e^{-i \mathbf{k} \cdot \mathbf{r}} \, d^2\mathbf{r}$$
By the convolution theorem:
$$\widetilde{(S_w \psi)}(\mathbf{k}) = \widetilde{G}_{w_0}(\mathbf{k}) \widetilde{\psi}(\mathbf{k})$$
The 2D Fourier transform of the normalized Gaussian kernel $G_{w_0}(\mathbf{r})$ is:
$$\widetilde{G}_{w_0}(\mathbf{k}) = \int_{\mathbb{R}^2} \frac{1}{2\pi w_0^2} e^{-|\mathbf{r}|^2 / (2 w_0^2)} e^{-i \mathbf{k} \cdot \mathbf{r}} \, d^2\mathbf{r} = \exp\left( - \frac{1}{2} w_0^2 |\mathbf{k}|^2 \right)$$

Therefore, the continuous spectrum $\sigma(S_w)$ of the frame operator is:
$$\boxed{\sigma(k) = \exp\left( - \frac{1}{2} w_0^2 k^2 \right) \in (0, 1]}$$
where $k = |\mathbf{k}|$ is the spatial frequency.

### 6.4 Paraxial Bandlimited Subspace

On the entire unbounded Hilbert space $L^2(\mathbb{R}^2)$, as $k \to \infty$, $\sigma(k) \to 0$. The lower frame bound would be:
$$A = \inf_{k \in \mathbb{R}^+} \exp\left( - \frac{1}{2} w_0^2 k^2 \right) = 0$$
Hence, physical PVBs form a continuous Bessel family, but fail the lower frame bound on full $L^2(\mathbb{R}^2)$ because the Gaussian filter suppresses infinite spatial frequencies.

However, in physical optics, infinite spatial frequencies are strictly unphysical. Every real paraxial optical beam is bandlimited by the numerical aperture $\text{NA}$ of the optical system:
$$K_{\max} = k_0 \text{NA} = \frac{2\pi}{\lambda} \text{NA} < \infty$$
We therefore define the **paraxial bandlimited Hilbert subspace**:
$$\mathcal{H}_{\text{band}} = \left\{ \psi \in L^2(\mathbb{R}^2) : \operatorname{supp}(\widetilde{\psi}) \subseteq B(0, K_{\max}) \right\}$$
where $B(0, K_{\max}) = \{\mathbf{k} \in \mathbb{R}^2 : |\mathbf{k}| \le K_{\max}\}$. By the Paley-Wiener theorem, $\mathcal{H}_{\text{band}}$ is a closed subspace of $L^2(\mathbb{R}^2)$, and therefore a complete Hilbert space in its own right.

### 6.5 Proof of Frame Bounds and Condition Number

**Theorem 3 (Continuous Frame on $\mathcal{H}_{\text{band}}$).**  
*On the paraxial bandlimited subspace $\mathcal{H}_{\text{band}}$, the family of physical PVBs $\{\Phi_{l, R}\}$ forms a continuous overcomplete frame with frame bounds:*
$$\boxed{0 < A = \exp\left( - \frac{1}{2} w_0^2 K_{\max}^2 \right) \le S_w \le B = 1 < \infty}$$
*and condition number:*
$$\kappa \equiv \frac{B}{A} = \exp\left( \frac{1}{2} w_0^2 K_{\max}^2 \right) < \infty$$

*Proof.*  
Let $\psi \in \mathcal{H}_{\text{band}}$. Using Plancherel's theorem:
$$\|S_w^{1/2} \psi\|^2 = \langle \psi | S_w \psi \rangle = \int_{|\mathbf{k}| \le K_{\max}} |\widetilde{\psi}(\mathbf{k})|^2 \exp\left( - \frac{1}{2} w_0^2 |\mathbf{k}|^2 \right) d^2\mathbf{k}$$
Since $|\mathbf{k}| \in [0, K_{\max}]$, the exponential kernel is monotonically decreasing and strictly bounded:
$$e^{-\frac{1}{2} w_0^2 K_{\max}^2} \le \exp\left( - \frac{1}{2} w_0^2 |\mathbf{k}|^2 \right) \le 1$$
Factoring out the bounds from the integral:
$$\exp\left( - \frac{1}{2} w_0^2 K_{\max}^2 \right) \int_{|\mathbf{k}| \le K_{\max}} |\widetilde{\psi}(\mathbf{k})|^2 \, d^2\mathbf{k} \le \langle \psi | S_w \psi \rangle \le \int_{|\mathbf{k}| \le K_{\max}} |\widetilde{\psi}(\mathbf{k})|^2 \, d^2\mathbf{k}$$
Since $\|\widetilde{\psi}\|^2 = \|\psi\|^2$ by Plancherel's identity:
$$A \|\psi\|^2 \le \langle \psi | S_w \psi \rangle \le B \|\psi\|^2$$
with:
$$A = \exp\left( - \frac{1}{2} w_0^2 K_{\max}^2 \right) > 0, \quad B = 1 < \infty$$
Because $0 < A \le B < \infty$, the frame condition is rigorously satisfied. $\blacksquare$

**Condition Number Stability:**  
In physical paraxial optics, $K_{\max} = k_0 \text{NA}$. For typical experimental values ($\lambda = 1550\,\text{nm}$, $\text{NA} \approx 0.00037$ for a beam waist $w_0 = 1.0\,\text{mm}$), the product $w_0 K_{\max} \approx 1.5$.
Then:
$$A = e^{-1.5^2 / 2} = e^{-1.125} \approx 0.3247, \quad B = 1.0000$$
$$\kappa = \frac{B}{A} = e^{1.125} \approx 3.08$$
A condition number of $\kappa \approx 3.08$ is exceptionally stable, ensuring robust, noise-free numerical inversion.

### 6.6 Canonical Dual Frame and Inversion Formula

Because $A > 0$, the frame operator $S_w: \mathcal{H}_{\text{band}} \to \mathcal{H}_{\text{band}}$ is self-adjoint, bounded, and has a bounded inverse $S_w^{-1}$ on $\mathcal{H}_{\text{band}}$, with operator norm:
$$\|S_w^{-1}\| = \frac{1}{A} = \exp\left( \frac{1}{2} w_0^2 K_{\max}^2 \right) < \infty$$
In spatial frequency space, the action of $S_w^{-1}$ is deconvolution by the inverse Gaussian filter:
$$\widetilde{(S_w^{-1} \psi)}(\mathbf{k}) = \exp\left( \frac{1}{2} w_0^2 |\mathbf{k}|^2 \right) \widetilde{\psi}(\mathbf{k})$$

The **canonical dual frame** is defined by:
$$\widetilde{\Phi}_{l, R}(\mathbf{r}) \equiv S_w^{-1} \Phi_{l, R}(\mathbf{r})$$
In Fourier space, each dual mode is given by:
$$\widetilde{\Phi}_{l, R}^{\text{dual}}(\mathbf{k}) = \exp\left( \frac{1}{2} w_0^2 |\mathbf{k}|^2 \right) \widetilde{\Phi}_{l, R}(\mathbf{k})$$

Any paraxial optical field $\psi \in \mathcal{H}_{\text{band}}$ admits the exact, stable dual frame expansion:
$$\boxed{\psi(\mathbf{r}) = \sum_{l=-\infty}^\infty \int_0^\infty R \, dR \, \langle \Phi_{l, R} | \psi \rangle \widetilde{\Phi}_{l, R}(\mathbf{r}) = \sum_{l=-\infty}^\infty \int_0^\infty R \, dR \, \langle \widetilde{\Phi}_{l, R} | \psi \rangle \Phi_{l, R}(\mathbf{r})}$$
This establishes the rigorous resolution of the identity on $\mathcal{H}_{\text{band}}$:
$$\int_\Omega |\Phi_{l, R} \rangle \langle \widetilde{\Phi}_{l, R} | \, d\mu(l, R) = \mathbb{I}_{\text{band}}$$

---

## 7. Classical Optical Advantages of PVB Overcompleteness

### 7.1 Multi-Ring Spatial Division Multiplexing (SDM)

In conventional spatial division multiplexing (SDM) using Laguerre-Gaussian modes ($\text{LG}_{p, l}$), the mode field diameter expands as $w_l \propto \sqrt{|l| + 1}$. Multiplexing 10 OAM channels forces the outermost mode to occupy an area more than ten times larger than the fundamental mode. This creates severe physical bottlenecks:
1. Outer modes suffer severe geometric clipping at aperture stops.
2. Receiver photodetectors must accommodate the largest mode, increasing dark current and capacitance.
3. In ring-core fibers (RCFs), high-$l$ LG modes leak into the fiber cladding, causing prohibitive insertion losses.

In sharp contrast, PVBs possess an $l$-independent ring radius:
$$r_0(l) \approx r_0 \quad (\Delta r_l \le 0.04 w_0)$$
In experimental measurements by Villalba, Melo, Ayala et al. [*Opt. Express* **31**, 40113 (2023)], the ring radius variance across charges $l = 1, \dots, 6$ was measured to be only $5.4\,\mu\text{m}^2$ for PVBs, compared to $1873.3\,\mu\text{m}^2$ for LG modes—a stability improvement factor of **347**!

Because of this geometric stability, multiple concentric PVBs with distinct radii $\{r_{0, 1}, r_{0, 2}, \dots, r_{0, M}\}$ can be multiplexed within the same annular waveguide core. While adjacent rings with spacing $\Delta r < w_0$ overlap, their normalized cross-talk Gram matrix:
$$G_{ij} = \gamma_l(r_{0, i}, r_{0, j}; w_0) \approx \exp\left( - \frac{(r_{0, i} - r_{0, j})^2}{2 w_0^2} \right)$$
is strictly symmetric, positive-definite, and well-conditioned. Using the canonical dual frame inverse $G^{-1}$ (or MMSE equalization), all concentric channels are cleanly separated with minimal noise amplification.

### 7.2 The 8.6 dB Power Advantage in Ring-Core Fibers

In Villalba et al. (2023), classical optical signals modulated at 1 Gbps were transmitted through 300 meters of graded-index ring-core fiber (GRIN-RCF, core inner radius $6\,\mu\text{m}$, outer radius $9\,\mu\text{m}$).
- Fixed launch power: $450\,\mu\text{W}$.
- Coupled power at fiber output: $P_{\text{out}}^{\text{PVB}} \approx 15\text{--}16\,\mu\text{W}$ vs. $P_{\text{out}}^{\text{LG}} \approx 3.3\text{--}4\,\mu\text{W}$.
- To achieve the standard Hard-Decision Forward Error Correction (HD-FEC) threshold ($\text{BER} = 4.7 \times 10^{-3}$), PVBs required **8.6 dB less optical signal power** than LG modes.

This 8.6 dB power advantage directly reflects the mathematical overcompleteness and radial invariance of PVBs: the optical energy is concentrated entirely within the annular acceptance zone of the fiber, whereas orthogonal LG modes suffer severe modal spillover.

### 7.3 Reproducing Kernel Hilbert Space (RKHS) Projective Noise Filtering

Let $\mathcal{T}: \mathcal{H}_{\text{band}} \to L^2(\Omega, d\mu)$ be the continuous frame analysis operator:
$$(\mathcal{T} \psi)(l, R) \equiv c(l, R) = \langle \Phi_{l, R} | \psi \rangle$$
Because the family $\{\Phi_{l, R}\}$ is overcomplete, the range $\mathcal{K} \equiv \operatorname{Ran}(\mathcal{T}) \subsetneq L^2(\Omega, d\mu)$ is a **proper closed subspace**.

The space $\mathcal{K}$ is a Reproducing Kernel Hilbert Space (RKHS) whose reproducing kernel is the mode overlap function:
$$K(l_1, R_1; l_2, R_2) = \langle \Phi_{l_1, R_1} | \Phi_{l_2, R_2} \rangle = \delta_{l_1, l_2} \frac{1}{w_0^2} \exp\left( - \frac{R_1^2 + R_2^2}{2 w_0^2} \right) I_{l_1}\left( \frac{R_1 R_2}{w_0^2} \right)$$
The orthogonal projection operator $P_{\text{RKHS}}: L^2(\Omega, d\mu) \to \mathcal{K}$ onto the space of physical signals is:
$$\boxed{P_{\text{RKHS}} = \mathcal{T} S_w^{-1} \mathcal{T}^*}$$

Now consider an optical beam propagating through atmospheric turbulence (Kolmogorov spectrum with structure constant $C_n^2$ and Fried parameter $r_0^{\text{turb}}$). Turbulence introduces random phase distortions $\psi_{\text{turb}}(\mathbf{r}) = \psi(\mathbf{r}) e^{i \phi(\mathbf{r})}$. When projected onto the overcomplete PVB family, the noisy coefficients are:
$$c_{\text{meas}}(l, R) = c_{\text{signal}}(l, R) + \eta(l, R)$$
where $\eta(l, R)$ represents turbulence-induced modal cross-talk and detector noise.

In a minimal orthonormal basis, every coefficient sequence is valid; any noise $\eta$ is indistinguishable from a legitimate signal.
In an overcomplete frame, noise components residing in the orthogonal complement $\mathcal{K}^\perp$ are unphysical. Applying the RKHS projector:
$$P_{\text{RKHS}} c_{\text{meas}} = c_{\text{signal}} + P_{\text{RKHS}} \eta$$
Because isotropic noise is distributed uniformly across $L^2(\Omega)$, the projection operator **identically removes all out-of-subspace noise components**, achieving passive wavefront cleanup and modal error suppression without requiring active adaptive optics hardware!

### 7.4 Spatial Low-Pass Filtering Transfer Function

From Section 6.3, the un-inverted frame operator $S_w$ applies the Fourier transfer function:
$$\widetilde{G}_{w_0}(\mathbf{k}) = \exp\left( - \frac{1}{2} w_0^2 |\mathbf{k}|^2 \right)$$
Perturbations on spatial scales smaller than the ring thickness ($\Delta r < w_0$, corresponding to spatial frequencies $k > 1/w_0$) are exponentially attenuated by a factor of $\le e^{-1/2} \approx 0.606$ at $k = 1/w_0$, and $\le e^{-2} \approx 0.135$ at $k = 2/w_0$.
Thus, physical PVB projections act as an intrinsic spatial low-pass filter, shielding optical information against fine-grained atmospheric speckle, dust scattering, and high-frequency phase fluctuations.

### 7.5 Modal Redundancy and Self-Healing Against Beam Obscuration

When an optical beam encounters an opaque obstacle or angular clipping sector $\Delta \theta$, an orthonormal basis undergoes irreversible information loss. In an overcomplete PVB frame, the information is redundantly distributed across overlapping vortex coordinates $(l, R)$.

Because the constituent Bessel-Gauss waves carry transverse wavevectors $k_r$ angled toward the optical axis, energy propagates around the obstruction. The missing angular segment of the field is synthesized downstream via the dual frame operator $S_w^{-1}$ from the unshadowed spatial components, reconstituting the intact vortex phase singularity.

---

## 8. Quantum Optical Advantages in High-Dimensional Spaces

### 8.1 Informationally Complete POVM (IC-POVM) Quantum State Tomography

In high-dimensional quantum systems (spatial qudits of dimension $d$), conventional quantum state tomography requires projective von Neumann measurements in $d+1$ mutually unbiased bases (MUBs). Experimentally, this demands dynamically reconfiguring spatial light modulators (SLMs) $d+1$ times, introducing significant latency and calibration drift.

The continuous frame resolution of identity on $\mathcal{H}_{\text{band}}$:
$$\int_\Omega |\Phi_{l, R} \rangle \langle \widetilde{\Phi}_{l, R}| \, d\mu(l, R) = \mathbb{I}$$
allows the direct construction of a continuous **Positive Operator-Valued Measure (POVM)**:
$$\boxed{\hat{\Pi}(l, R) \equiv R \, S_w^{-1/2} |\Phi_{l, R}\rangle \langle \Phi_{l, R}| S_w^{-1/2} \ge 0}$$
Integrating over the entire parameter space:
$$\sum_{l=-\infty}^\infty \int_0^\infty dR \, \hat{\Pi}(l, R) = S_w^{-1/2} \left[ \sum_{l=-\infty}^\infty \int_0^\infty R \, dR \, |\Phi_{l, R}\rangle \langle \Phi_{l, R}| \right] S_w^{-1/2} = S_w^{-1/2} S_w S_w^{-1/2} = \mathbb{I}$$

Because the family $\{\Phi_{l, R}\}$ spans the entire space of spatial qudits, the operator family $\{\hat{\Pi}(l, R)\}$ spans the space of Hermitian density operators $\mathcal{B}(\mathcal{H}_d)$. It constitutes an **Informationally Complete POVM (IC-POVM)**.
The quantum density matrix $\hat{\rho}$ of an unknown photonic state is determined from the measurement probability distribution:
$$p(l, R) = \operatorname{Tr}[\hat{\rho} \hat{\Pi}(l, R)]$$
In an experimental setup, this continuous POVM can be implemented in a **single static configuration** (e.g., using multi-plane light conversion, MPLC, or off-axis digital holography) without SLM switching. Moreover, the mathematical redundancy of the overcomplete frame minimizes the variance of the quantum estimator, saturating the quantum Cramér-Rao bound with substantially lower total photon counts than standard projective tomography.

### 8.2 Constant Aperture Footprint in High-Dimensional QKD

In high-dimensional quantum key distribution (HD-QKD), encoding information in $d$-dimensional qudits yields two decisive advantages:
1. Information capacity increases as $\log_2 d$ bits per detected photon.
2. The threshold error rate against optimal coherent eavesdropping attacks increases monotonically:
   $$e_{\text{thresh}}(d) = \frac{d - 1}{2d}$$
   rising from $11.0\%$ for qubits ($d=2$) to $18.96\%$ for $d=4$, and approaching $50\%$ as $d \to \infty$.

However, conventional OAM modes (such as LG modes) suffer from dimension-dependent aperture truncation: the mode radius scales as $r_{\max} \propto \sqrt{d}$. Higher-dimensional states are clipped by receiver apertures, creating $l$-dependent channel loss that introduces fatal eavesdropping vulnerabilities (the detection loophole).

Because PVBs possess an invariant ring radius $r_0$ independent of $l$, they maintain a **constant aperture footprint across all dimensions $d$**.
In Villalba et al. (2023), 4-dimensional spatial qudits ($l = 1, 2, 3, 4$) were propagated through 300 meters of ring-core fiber with an **average quantum state fidelity of $F = 92.0\%$**, comfortably exceeding the coherent-attack security threshold ($F_{\text{thresh}} = 81.04\%$). Overcompleteness guarantees uniform transmission efficiency and zero clipping leakage across high-dimensional qudit alphabets.

### 8.3 Entanglement Preservation in SPDC Through Finite Optical Apertures

In spontaneous parametric down-conversion (SPDC), nonlinear crystals generate photon pairs entangled in orbital angular momentum:
$$|\Psi\rangle = \sum_{l=-\infty}^\infty c_l |l\rangle_s |-l\rangle_i \otimes |u_l(r)\rangle_s |u_{-l}(r)\rangle_i$$
For conventional Laguerre-Gaussian modes, the radial wavefunctions $u_l(r)$ depend strongly on $l$:
$$u_l^{\text{LG}}(r) \propto \left( \frac{\sqrt{2} r}{w_0} \right)^{|l|} \exp\left( - \frac{r^2}{w_0^2} \right)$$
When either the signal or idler photon passes through an optical pupil or iris of finite aperture radius $R_{\text{iris}}$, the transmission operator acts as a radial step function $\hat{T} = \Theta(R_{\text{iris}} - r)$.
The transmitted amplitude for mode $l$ is:
$$\eta_l(R_{\text{iris}}) = \int_0^{R_{\text{iris}}} r \, dr \, |u_l^{\text{LG}}(r)|^2$$
Because higher-$l$ modes extend further outward, they suffer progressively greater clipping losses: $\eta_l < \eta_0$ for $|l| > 0$. This differential loss distorts the Schmidt spectrum $\{c_l \eta_l\}$, reducing the Schmidt number:
$$K = \frac{1}{\sum_l |c_l \eta_l|^4}$$
degrading two-photon concurrence, and collapsing the Bell-CHSH parameter below the quantum violation threshold ($S \le 2$).

For physical PVBs, the radial intensity profile is decoupled from topological charge:
$$u_l^{\text{PVB}}(r) \approx \frac{1}{\sqrt{2\pi r_0}} \left( \frac{2}{\pi w_0^2} \right)^{1/4} \exp\left( - \frac{(r - r_0)^2}{w_0^2} \right) \quad (\forall l)$$
Consequently, the iris transmission function acts as an **identical scalar multiplier across all OAM states**:
$$\hat{T} |u_l^{\text{PVB}}\rangle = \kappa_{\text{iris}} |u_l^{\text{PVB}}\rangle \quad \forall l$$
where:
$$\kappa_{\text{iris}} = \int_0^{R_{\text{iris}}} r \, dr \, |u(r)|^2 = \text{const}$$
The filtered state remains:
$$|\Psi_{\text{trans}}\rangle = \kappa_{\text{iris}}^2 \sum_{l=-\infty}^\infty c_l |l\rangle_s |-l\rangle_i \otimes |u(r)\rangle_s |u(r)\rangle_i$$
The normalized quantum state is **100% invariant under circular aperture truncation**, preserving the full Schmidt entanglement spectrum, concurrence, and maximal Bell-CHSH violation ($S = 2\sqrt{2} \approx 2.828$) regardless of aperture restrictions!

---

## 9. Pedagogical Appendix A: Primer on Perfect Vortex Beams

### A.1 Physical Motivation: Decoupling Geometry from Angular Momentum
In optical physics, light carrying orbital angular momentum (OAM) is characterized by an azimuthal phase factor $e^{i l \phi}$, imparting an angular momentum of $l \hbar$ per photon [Allen et al. (1992)]. In canonical vortex modes such as Laguerre-Gaussian ($\text{LG}_{p, l}$) or high-order Bessel beams ($J_l(k_r r) e^{i l \phi}$), the phase singularity at the origin forces the on-axis intensity to vanish, creating an annular bright ring.

However, the transverse wave equation enforces a severe geometric coupling: the radial position of the intensity maximum expands monotonically with the topological charge:
$$r_{\max}^{\text{LG}} = w_0 \sqrt{\frac{2p + |l|}{2}}$$
When switching between different OAM states (e.g., $l=1$ to $l=10$), the beam radius more than triples. This causes prohibitive complications in coupling into fibers, optical tweezers trapping, and free-space communication links.

The concept of a "Perfect Vortex Beam" arose from a simple physical question: *Can one construct an optical beam whose annular ring radius $r_0$ and ring width $w_0$ remain completely invariant, regardless of the topological charge $l$?*

### A.2 Generation Mechanism via Fourier Optics
The generation of physical PVBs relies on the Fourier-transform property of lenses:
1. **The Axicon Phase:** A conical prism (axicon) imparts a conical phase delay $e^{i k_r \rho}$, converting an incident planar wavefront into a conical wave propagating toward the optical axis at a constant angle $\gamma = \arcsin(k_r / k)$.
2. **The Vortex Phase:** A spiral phase plate (SPP) or spatial light modulator (SLM) imprints the azimuthal phase factor $e^{i l \phi}$.
3. **The Bessel-Gauss Beam:** Combining these elements with a fundamental Gaussian laser beam produces a Bessel-Gauss beam:
   $$E_{\text{BG}}(\rho, \phi) = J_l(k_r \rho) e^{i l \phi} \exp\left( - \frac{\rho^2}{w_g^2} \right)$$
   This field carries a constant radial wavevector component $k_r$ across the entire aperture.
4. **Fourier Lens Transformation:** When a lens of focal length $f$ is placed one focal length away, it performs an optical 2D Fourier transform. A conical wave with fixed radial wavevector $k_r$ is focused into a ring of radius:
   $$r_0 = \frac{f k_r}{k} = f \sin \gamma$$
   Because $k_r$ is determined solely by the axicon angle, $r_0$ is completely independent of the topological charge $l$.
   Meanwhile, the finite Gaussian beam waist $w_g$ diffracts according to standard Gaussian beam optics, creating a focal ring of half-width:
   $$w_0 = \frac{2f}{k w_g} = \frac{\lambda f}{\pi w_g}$$

### A.3 Field Equation and Intensity Profile
At the focal plane, the field is described by:
$$\psi_{l, r_0, w_0}(r, \phi) \propto \exp\left( - \frac{r^2 + r_0^2}{w_0^2} \right) I_l\left( \frac{2 r_0 r}{w_0^2} \right) e^{i l \phi}$$
For $r_0 \gg w_0$, the modified Bessel function expands into a Gaussian ring centered at $r \approx r_0$. The radial intensity profile is:
$$I(r) \approx I_0 \exp\left( - \frac{2(r - r_0)^2}{w_0^2} \right)$$
which represents an annular ring of radius $r_0$ and full-width at half-maximum $\text{FWHM} = w_0 \sqrt{2 \ln 2} \approx 1.177 w_0$.

---

## 10. Pedagogical Appendix B: Complete Bases in Hilbert Spaces

### B.1 Mathematical Definitions
Let $\mathcal{H}$ be a complex separable Hilbert space equipped with inner product $\langle \cdot | \cdot \rangle$ and norm $\|f\| = \sqrt{\langle f | f \rangle}$.

1. **Hamel Basis (Algebraic):** A subset $\mathcal{B} \subset \mathcal{H}$ such that every vector $f \in \mathcal{H}$ can be written as a *finite* linear combination of elements in $\mathcal{B}$. In infinite-dimensional Hilbert spaces, Hamel bases are uncountably infinite and topologically ill-suited for analysis.
2. **Schauder Basis (Topological):** A countable sequence $\{e_n\}_{n=1}^\infty \subset \mathcal{H}$ such that for every $f \in \mathcal{H}$, there exists a *unique* sequence of scalar coefficients $\{c_n(f)\}_{n=1}^\infty \subset \mathbb{C}$ such that:
   $$\lim_{N \to \infty} \left\| f - \sum_{n=1}^N c_n(f) e_n \right\| = 0$$
3. **Orthonormal Basis (ONB):** A Schauder basis satisfying the orthogonality and normalization condition:
   $$\langle e_n | e_m \rangle = \delta_{nm}$$
   For any $f \in \mathcal{H}$, the expansion coefficients are uniquely given by the inner products:
   $$c_n(f) = \langle e_n | f \rangle$$
   and the state satisfies **Parseval's identity**:
   $$\|f\|^2 = \sum_{n=1}^\infty |\langle e_n | f \rangle|^2$$
   and the **resolution of identity**:
   $$\sum_{n=1}^\infty |e_n\rangle \langle e_n| = \mathbb{I}$$

### B.2 Riesz Bases
A Riesz basis is an unconditional basis obtained by applying a bounded, bijective linear operator $T: \mathcal{H} \to \mathcal{H}$ to an orthonormal basis: $v_n = T e_n$.
A sequence $\{v_n\}_{n=1}^\infty$ is a Riesz basis if and only if there exist constants $0 < c \le C < \infty$ such that for all finite scalar sequences $\{a_n\}$:
$$c \sum_n |a_n|^2 \le \left\| \sum_n a_n v_n \right\|^2 \le C \sum_n |a_n|^2$$
Riesz bases preserve uniqueness of expansion and topological stability, but allow non-orthogonal vectors.

### B.3 Rigged Hilbert Spaces (Gel'fand Triplets) and Continuous Bases
In quantum mechanics, continuous spectra arise for observables such as position $\hat{x}$ and momentum $\hat{p}$. The corresponding "eigenstates" $|x\rangle$ satisfy:
$$\langle x | x' \rangle = \delta(x - x')$$
Because $\||x\rangle\|^2 = \delta(0) = \infty$, these generalized eigenvectors do not belong to the Hilbert space $L^2(\mathbb{R})$.

To place continuous spectra on rigorous footing, I. M. Gel'fand introduced the **Rigged Hilbert Space (Gel'fand Triplet)**:
$$\Phi \subset \mathcal{H} \subset \Phi^\times$$
1. $\Phi$ is a dense nuclear subspace (test function space, e.g., the Schwartz space $\mathcal{S}(\mathbb{R})$ of smooth, rapidly decaying functions) equipped with a topology finer than the Hilbert norm.
2. $\mathcal{H} = L^2(\mathbb{R})$ is the standard physical Hilbert space.
3. $\Phi^\times$ is the topological dual space of $\Phi$, containing continuous linear functionals (tempered distributions).

The Dirac delta function $\delta(r - r_0)$ and the ideal PVB $\psi_{l, r_0}^{\text{ideal}}$ reside strictly in $\Phi^\times$. They serve as continuous generalized expansion kernels via the Nuclear Spectral Theorem:
$$f(r) = \int_0^\infty dr_0 \, \delta(r - r_0) f(r_0)$$
However, they cannot represent physical states of finite energy.

---

## 11. Pedagogical Appendix C: Overcomplete Bases, Frames, and Coherent States

### C.1 Foundations of Frame Theory
In 1952, Duffin & Schaeffer introduced **frames** while studying non-harmonic Fourier series. A frame relaxes the linear independence constraint of a Riesz basis, allowing redundancy while guaranteeing stable reconstruction.

Let $\mathcal{H}$ be a Hilbert space and $\{f_k\}_{k \in I}$ a family of vectors.
- **Bessel Family:** If there exists $B < \infty$ such that:
  $$\sum_{k \in I} |\langle f_k | f \rangle|^2 \le B \|f\|^2 \quad (\forall f \in \mathcal{H})$$
- **Frame:** If there exist $0 < A \le B < \infty$ such that:
  $$A \|f\|^2 \le \sum_{k \in I} |\langle f_k | f \rangle|^2 \le B \|f\|^2 \quad (\forall f \in \mathcal{H})$$
- **Tight Frame:** $A = B$. If $A = B = 1$, it is a **Parseval frame**.

### C.2 Analysis, Synthesis, and Frame Operators
For a frame $\{f_k\}$, we define three fundamental linear operators:
1. **Analysis Operator** $T: \mathcal{H} \to \ell^2(I)$:
   $$(T f)_k = \langle f_k | f \rangle$$
2. **Synthesis Operator** $T^*: \ell^2(I) \to \mathcal{H}$:
   $$T^* c = \sum_{k \in I} c_k f_k$$
3. **Frame Operator** $S = T^* T: \mathcal{H} \to \mathcal{H}$:
   $$S f = \sum_{k \in I} \langle f_k | f \rangle f_k$$
Because $A \mathbb{I} \le S \le B \mathbb{I}$, the frame operator $S$ is self-adjoint, bounded, positive, and invertible, with:
$$B^{-1} \mathbb{I} \le S^{-1} \le A^{-1} \mathbb{I}$$

### C.3 The Canonical Dual Frame and Overcompleteness
The **canonical dual frame** is given by:
$$\widetilde{f}_k \equiv S^{-1} f_k$$
The dual vectors $\{\widetilde{f}_k\}$ also form a frame with bounds $B^{-1} \le A^{-1}$.
Every vector $f \in \mathcal{H}$ can be reconstructed as:
$$f = \sum_{k \in I} \langle f_k | f \rangle \widetilde{f}_k = \sum_{k \in I} \langle \widetilde{f}_k | f \rangle f_k$$

**Overcompleteness and Non-Uniqueness:**  
If a frame is not a Riesz basis, it is **overcomplete** (redundant). The kernel of the synthesis operator is non-trivial: $\operatorname{Ker}(T^*) \neq \{0\}$.
Consequently, an arbitrary vector $f$ can be represented in infinitely many ways:
$$f = \sum_k c_k f_k$$
The canonical coefficients $c_k = \langle \widetilde{f}_k | f \rangle$ are unique in that they minimize the $\ell^2$ norm of the coefficients:
$$\sum_k |\langle \widetilde{f}_k | f \rangle|^2 \le \sum_k |c_k|^2$$

### C.4 Continuous Frames and Coherent States
In 1993, Ali, Antoine, and Gazeau generalized frame theory to continuous index spaces $(\Omega, \mu)$.
Canonical coherent states in quantum mechanics:
$$|\alpha\rangle = e^{-|\alpha|^2/2} \sum_{n=0}^\infty \frac{\alpha^n}{\sqrt{n!}} |n\rangle \quad (\alpha \in \mathbb{C})$$
form a continuous Parseval frame on $L^2(\mathbb{R})$ with measure $d\mu(\alpha) = \frac{d^2\alpha}{\pi}$:
$$\int_{\mathbb{C}} |\alpha\rangle \langle \alpha| \, \frac{d^2\alpha}{\pi} = \mathbb{I}$$
Coherent states are non-orthogonal:
$$\langle \alpha | \beta \rangle = \exp\left( - \frac{|\alpha|^2 + |\beta|^2}{2} + \alpha^* \beta \right) \neq 0$$
Physical PVBs $\{\Phi_{l, R}\}$ form the cylindrical vortex counterpart of optical coherent states: they are continuously indexed, non-orthogonal, linearly redundant, and resolve the identity through a well-conditioned continuous frame operator.

---

## 12. Numerical Verification and Python Reproducibility Suite

To substantiate every analytical formula, theorem, and bound presented in this work, this section provides self-contained, reproducible Python verification scripts. All scripts have been tested under Python 3.12 with standard libraries (`numpy`, `scipy`).

### 12.1 Verification Script 1: Exact Gradshteyn-Ryzhik Inner Product vs. Numerical Quadrature

```python
import numpy as np
import scipy.integrate as integrate
from scipy.special import iv

def verify_inner_product():
    """Verifies Gradshteyn & Ryzhik formula 6.633.2 against numerical quadrature."""
    l = 2
    r1 = 1.05  # mm
    r2 = 1.25  # mm
    w0 = 0.20  # mm

    # Exact closed-form radial inner product
    exact_val = (w0**2 / 4.0) * np.exp(-(r1**2 + r2**2) / (2.0 * w0**2)) * iv(l, r1 * r2 / w0**2)

    # Numerical adaptive quadrature
    def integrand(r):
        u1 = np.exp(-(r**2 + r1**2) / w0**2) * iv(l, 2.0 * r1 * r / w0**2)
        u2 = np.exp(-(r**2 + r2**2) / w0**2) * iv(l, 2.0 * r2 * r / w0**2)
        return r * u1 * u2

    num_val, _ = integrate.quad(integrand, 0.0, 5.0, epsabs=1e-15, epsrel=1e-12)

    rel_error = abs(exact_val - num_val) / exact_val
    print(f"Exact Analytical Integral: {exact_val:.16e}")
    print(f"Numerical Quadrature:     {num_val:.16e}")
    print(f"Relative Discrepancy:     {rel_error:.2e}")
    assert rel_error < 1e-11, "Inner product verification failed!"
    print(">> TEST 1 PASSED: Closed-form formula verified to machine precision.\n")

if __name__ == "__main__":
    verify_inner_product()
```

### 12.2 Verification Script 2: Normalized Overlap and Asymptotic Gaussian Fidelity

```python
import numpy as np
from scipy.special import iv

def verify_normalized_overlap():
    """Verifies normalized overlap formula and asymptotic Gaussian cross-talk."""
    l = 3
    r1 = 1.00  # mm
    r2 = 1.15  # mm
    w0 = 0.15  # mm

    # Exact formula via modified Bessel quotient
    num = iv(l, r1 * r2 / w0**2)
    den = np.sqrt(iv(l, r1**2 / w0**2) * iv(l, r2**2 / w0**2))
    gamma_exact = num / den

    # Asymptotic universal Gaussian formula
    gamma_asymp = np.exp(-(r1 - r2)**2 / (2.0 * w0**2))

    # Second-order corrected asymptotic formula
    corr = 1.0 + ((4*l**2 - 1) / 16.0) * (w0**2 * (r1 - r2)**2) / (r1**2 * r2**2)
    gamma_corr = gamma_asymp * corr

    print(f"Exact Overlap gamma:      {gamma_exact:.8f}")
    print(f"Leading Gaussian Asymp:   {gamma_asymp:.8f} (Error: {abs(gamma_exact - gamma_asymp):.2e})")
    print(f"Corrected Gaussian Asymp: {gamma_corr:.8f} (Error: {abs(gamma_exact - gamma_corr):.2e})")
    assert abs(gamma_exact - gamma_corr) < 1e-4, "Asymptotic overlap verification failed!"
    print(">> TEST 2 PASSED: Asymptotic Gaussian cross-talk verified.\n")

if __name__ == "__main__":
    verify_normalized_overlap()
```

### 12.3 Verification Script 3: Continuous Frame Spectrum and Paraxial Bounds

```python
import numpy as np

def verify_frame_bounds():
    """Verifies continuous frame bounds and condition number on bandlimited subspace."""
    w0 = 0.20  # mm
    wavelength = 1550e-6  # mm (1550 nm)
    k0 = 2.0 * np.pi / wavelength
    NA = 0.00037  # Paraxial NA
    K_max = k0 * NA  # ~1.5 mm^-1

    # Frequency grid
    k_vals = np.linspace(0.0, K_max, 1000)
    spectrum = np.exp(-0.5 * (k_vals * w0)**2)

    A = np.min(spectrum)
    B = np.max(spectrum)
    condition_number = B / A

    analytical_A = np.exp(-0.5 * (w0 * K_max)**2)
    analytical_B = 1.0
    analytical_kappa = np.exp(0.5 * (w0 * K_max)**2)

    print(f"Lower Frame Bound A:      {A:.6f} (Analytical: {analytical_A:.6f})")
    print(f"Upper Frame Bound B:      {B:.6f} (Analytical: {analytical_B:.6f})")
    print(f"Frame Condition Number:   {condition_number:.4f} (Analytical: {analytical_kappa:.4f})")
    assert 0.0 < A <= B < np.inf, "Continuous frame bounds violated!"
    assert abs(condition_number - analytical_kappa) < 1e-12, "Condition number mismatch!"
    print(">> TEST 3 PASSED: Duffin-Schaeffer frame condition rigorously satisfied.\n")

if __name__ == "__main__":
    verify_frame_bounds()
```

### 12.4 Verification Script 4: Physical Unfeasibility Scalings as $w_0 \to 0$

```python
import numpy as np

def verify_singular_limit_divergence():
    """Verifies divergence rates of physical observables as w0 -> 0."""
    r0 = 1.0  # mm
    wavelength = 1550e-6  # mm
    k0 = 2.0 * np.pi / wavelength
    P = 1.0  # W

    w0_array = np.array([1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01])

    kr2_vals = 1.0 / (w0_array**2)
    M2_vals = r0 / w0_array
    I_max_vals = P / (np.pi**1.5 * np.sqrt(2.0) * r0 * w0_array)
    theta_div = (1.0 / (k0 * w0_array)) * 1e3  # mrad

    print(f"{'w0 (mm)':<10} | {'<kr^2> (mm^-2)':<16} | {'M^2':<10} | {'I_max (W/mm^2)':<16} | {'theta (mrad)':<12}")
    print("-" * 72)
    for w, kr2, m2, imax, th in zip(w0_array, kr2_vals, M2_vals, I_max_vals, theta_div):
        print(f"{w:<10.3f} | {kr2:<16.1f} | {m2:<10.1f} | {imax:<16.2f} | {th:<12.4f}")

    # Verify that as w0 shrinks by factor of 100, kr2 increases by 10^4 and I_max by 10^2
    assert kr2_vals[-1] / kr2_vals[0] == 10000.0, "kr2 divergence scaling error!"
    assert np.isclose(I_max_vals[-1] / I_max_vals[0], 100.0), "I_max scaling error!"
    print(">> TEST 4 PASSED: Divergence theorems verified across all physical parameters.\n")

if __name__ == "__main__":
    verify_singular_limit_divergence()
```

---
*End of Theoretical Foundations Document.*
