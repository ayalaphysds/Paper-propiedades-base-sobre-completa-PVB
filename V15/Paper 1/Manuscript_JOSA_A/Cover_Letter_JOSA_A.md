# Cover Letter — Submission to *Journal of the Optical Society of America A* (JOSA A)

**Date:** November 2026  
**To:** Editor-in-Chief, *Journal of the Optical Society of America A* (Optica Publishing Group)  
**From:** Sebastián Ayala, Independent Researcher, Cauquenes, Chile (`ayala.phys.ds@gmail.com`; ORCID: `0009-0003-7348-3883`)  
**Manuscript Title:** *Continuous Hilbert frame theory, paraxial propagation invariance, and exact Laguerre–Gaussian expansion of finite-width perfect optical vortex beams*  
**Preprint Identifier:** `arXiv:2611.XXXXX` *(insert live arXiv ID upon posting)*

---

Dear Editor-in-Chief,

I am pleased to submit the enclosed manuscript, *"Continuous Hilbert frame theory, paraxial propagation invariance, and exact Laguerre–Gaussian expansion of finite-width perfect optical vortex beams,"* for consideration as a Research Article in the *Journal of the Optical Society of America A*.

As a co-author of our experimental telecom ring-core fiber demonstration [Villalba *et al.*, *Opt. Express* **31**, 40113 (2023)] and our recent analysis of second-order moment equivalence for orbital angular momentum (OAM) eigenmodes [Ferreira *et al.*, *J. Opt.* **28**, 095601 (2026)], I developed this work to resolve four foundational mathematical-optics questions left open in Appendix D of our *Journal of Optics* study regarding finite-width physical perfect vortex beams (PVBs):

1. **Continuous Hilbert Frame Classification and Sharp Paley–Wiener Bounds:** While azimuthal OAM sectors decouple orthogonally, finite ring half-width $w > 0$ induces an isotropic Gaussian convolution frame operator $S_w = G_w * \cdot$ ($\widetilde{G}_w(k_\perp) = e^{-w^2 k_\perp^2/2}$) with optimal Bessel bound $B = 1$ on $L^2(\mathbb{R}^2)$ and sharp Paley–Wiener lower bound $A = \exp(-w^2 k_{\max}^2/2)$ on bandlimited optical subspaces $\mathcal{H}_{k_{\max}}$.
2. **Exact Paraxial Fresnel Propagation Invariance:** I derive the exact closed-form complex-waist Fresnel evolution $\Phi_{l,R}^{(z)}$ ($w_c^2(z) = w^2[1 + iz/z_R^{\mathrm{ring}}]$, verified against 40-digit Hankel quadrature to $5.3\times 10^{-23}$ and 2D FFT to $4.7\times 10^{-16}$), proving $[S_w, \mathcal{U}_z] = 0$ so that $S_w$ and all Paley–Wiener frame bounds remain strictly invariant across every propagation plane, while establishing the exact $\sigma_m^{+1}$ dimensional scaling of wavefront-compensated Gouy-plane analyzers.
3. **Tikhonov-Regularized Canonical Dual and Deconvolution Benchmark:** I prove that the regularized dual noise gain peaks at $(2\sqrt{\alpha_{\mathrm{reg}}})^{-1}$ at $k_{\mathrm{peak}} = w^{-1}\sqrt{\ln(1/\alpha_{\mathrm{reg}})}$, and validate the exact Parseval bias–variance tradeoff on noisy $\mathrm{LG}_{2,1}$ reconstruction ($258.6\times$ / $24.13\,\mathrm{dB}$ MSE suppression, matching 2D-FFT Monte Carlo simulations).
4. **Exact $(p+1)$-Term $\mathrm{LG}_{p,l}$ Expansion, WKB Arcsine Resolution Limit, and Discrete Gram Conditioning:** Extending the $p=0$ overlap to arbitrary radial orders $p \ge 0$ via Kummer's confluent hypergeometric transformation (verified to $1.08\times 10^{-15}$), I derive the universal WKB arcsine radial resolution limit $w_{\mathrm{crit}} \approx 0.5724\,w_0/\sqrt{2p+\abs{l}+1}$ and bound discrete multi-ring unit-normalized Gram matrices uniformly via the Jacobi-theta Toeplitz ratio $\vartheta_3/\vartheta_4$.

This manuscript is original, completely self-contained, has not been published previously, and is not under consideration by any other journal. There are no conflicts of interest, and all symbolic verification and figure-generation scripts are openly archived on GitHub/Zenodo.

**Suggested Independent Reviewers (no prior collaboration or conflict of interest):**
- **Prof. Andrew Forbes**, School of Physics, University of the Witwatersrand (structured light & finite-width PVBs)
- **Prof. Ebrahim Karimi**, Department of Physics, University of Ottawa (Laguerre–Gaussian radial quantum numbers & structured light)
- **Prof. Ravindra P. Singh**, Physical Research Laboratory, Ahmedabad (perfect optical vortex beams & propagation)
- **Prof. Karlheinz Gröchenig**, Faculty of Mathematics, University of Vienna (Gabor & continuous frame theory)

Thank you for your time and consideration.

Sincerely,  
**Sebastián Ayala**  
Independent Researcher, Cauquenes, Chile  
`ayala.phys.ds@gmail.com` | ORCID: `0009-0003-7348-3883`
