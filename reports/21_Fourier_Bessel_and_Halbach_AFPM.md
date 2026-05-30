# Fourier-Bessel Series & Halbach Arrays for Coreless AFPM

**Document Type:** Advanced Modeling Techniques  
**Version:** v1.0  
**Date:** May 30, 2026  
**Context:** Extension of Coreless AFPM Analytical Modeling (Document 20) for the NeuroFlux Quasi-3D Engine.

---

## 1. Fourier-Bessel Series for Coreless AFPM Modeling

### 1.1 Why Fourier-Bessel Series?

Standard quasi-2D or simple analytical methods struggle with:
- Strong radial (edge) effects in coreless machines (large air-gap).
- Curvature effects (especially at inner/outer radii).
- Complex permanent magnet shapes.

**Fourier-Bessel series** provide a powerful 3D analytical solution by expanding the magnetic field in terms of Bessel functions (radial) and Fourier series (angular + axial). This approach has shown excellent accuracy for coreless stator AFPM machines while remaining much faster than full 3D FEA.

Recent work (e.g., Rezaee-Alam et al., 2025) demonstrates its effectiveness for no-load field calculation in coreless AFPM.

### 1.2 Basic Mathematical Form

The magnetic field components in a coreless AFPM can be expressed using a combination of:

- **Bessel functions** \( J_n(kr) \) and \( Y_n(kr) \) for the radial dependence.
- **Fourier series** in the angular (\(\theta\)) and axial (\(z\)) directions.

For the magnetic scalar potential \(\phi_m\) in regions without current (air-gap and PM regions), the solution satisfies Laplace’s equation in cylindrical coordinates:

\[
\nabla^2 \phi_m = 0
\]

The general solution form used in coreless AFPM modeling is:

\[
\phi_m(r, \theta, z) = \sum_{n} \sum_{m} \left[ A_{nm} J_n(k_m r) + B_{nm} Y_n(k_m r) \right] \cdot \cos(n\theta) \cdot \cosh(k_m z) + \dots
\]

Boundary conditions are applied at the PM surfaces and rotor back-irons (if present) to determine the coefficients.

### 1.3 Implementation Considerations for the Engine

**Pros:**
- Good accuracy for 3D effects without meshing.
- Can handle different PM shapes and magnetization patterns.
- Suitable for quasi-3D multi-slice extension.

**Cons / Challenges:**
- More complex to implement and computationally heavier than simple Hague’s method.
- Requires careful handling of infinite series truncation and numerical stability (Bessel functions).
- Best used selectively (e.g., for final high-accuracy analytical evaluation or surrogate training data generation).

**Recommendation for NeuroFlux:**
- Use **Hague’s method + multi-slice** as the default fast path for coreless.
- Implement **Fourier-Bessel** as an optional higher-accuracy mode (activated via parameter or for specific validation cases).

---

## 2. Halbach Array Configurations in AFPM (Especially Coreless)

### 2.1 Why Halbach Arrays are Powerful in Coreless Designs

In coreless AFPM machines, there is no stator iron to help guide the flux. Halbach arrays on the rotor(s) offer significant advantages:

- **Higher air-gap flux density** in the desired direction.
- **Strong self-shielding** — reduced flux on the back side of the array, allowing thinner or eliminated rotor back-iron.
- Lower cogging and torque ripple in many configurations.
- Particularly beneficial in **single-stator double-rotor (SSDR) coreless** topologies.

### 2.2 Common Halbach Configurations for AFPM

| Configuration              | Description                                      | Benefit in Coreless                  | Modeling Impact |
|---------------------------|--------------------------------------------------|--------------------------------------|-----------------|
| **Single-sided Halbach**  | PMs arranged in Halbach pattern on one rotor    | Moderate flux concentration         | Moderate complexity |
| **Double-sided Halbach**  | Halbach on both rotors (opposing or aligned)    | Very high air-gap flux density      | Higher complexity |
| **Segmented / Partial**   | Only some poles use Halbach, others conventional| Balance of performance vs cost      | Easier partial implementation |
| **Ideal / Sinusoidal**    | Continuous ideal Halbach (theoretical)          | Maximum performance                 | Analytical friendly |

### 2.3 Impact on Analytical Modeling

Halbach arrays change the magnetization distribution \(\mathbf{M}(r, \theta, z)\). This affects the boundary conditions in the analytical field solution.

- For **Hague’s method**: The equivalent current sheet or magnetization must be adjusted to represent the rotating magnetization vector of the Halbach array.
- For **Fourier-Bessel series**: The coefficients are determined from the more complex magnetization pattern. The series naturally handles the higher harmonic content introduced by discrete Halbach segments.

**Implementation Tip:**
Create a `MagnetizationModel` class that can generate the appropriate magnetization distribution for conventional, Halbach, or custom arrays. This can then feed into either the Hague or Fourier-Bessel field solvers.

### 2.4 Practical Considerations

- **Discrete vs Ideal Halbach**: Real implementations use discrete magnet segments. The number of segments per pole significantly affects performance and modeling accuracy.
- **Back-iron reduction**: One of the biggest system-level benefits in coreless machines — thinner rotors reduce mass and inertia.
- **Demagnetization risk**: Halbach arrays can have higher local fields; care must be taken with magnet grade selection.

---

## 3. Combined Recommendation for the NeuroFlux Engine

For the Quasi-3D Analytical Engine (Document 19), the suggested roadmap is:

1. **Phase 1 (Current)**: Implement multi-slice Hague-based model for coreless (good speed/accuracy balance).
2. **Phase 2**: Add support for basic Halbach arrays (adjust magnetization model).
3. **Phase 3**: Implement Fourier-Bessel solver as a higher-accuracy optional path.
4. **Phase 4**: Enable combined Halbach + Fourier-Bessel for high-performance coreless designs.
5. **Phase 5**: Use the above to generate training data for surrogate models / digital twin ROMs.

This staged approach allows rapid progress while building toward high-fidelity analytical capability for coreless + Halbach machines.

---

## 4. References & Further Reading

- Rezaee-Alam et al. (2025): Analytical modeling of coreless stator AFPM using Fourier-Bessel series.
- Various papers on Halbach AFPM (especially for coreless and yokeless topologies).
- Document 12 (Mathematical Foundation) and Document 20 (Coreless Analytical Modeling) for base equations.

---

**This document provides the advanced modeling foundation needed to support high-performance coreless AFPM configurations (including Halbach) in the NeuroFlux analytical engine.**

**End of Fourier-Bessel and Halbach AFPM Exploration v1.0**