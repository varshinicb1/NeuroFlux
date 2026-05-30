# Coreless AFPM Analytical Modeling for the NeuroFlux Engine

**Document Type:** Deep Technical Modeling Study  
**Version:** v1.0  
**Date:** May 30, 2026  
**Purpose:** Provide detailed analytical modeling guidance for coreless AFPM topologies to support implementation of the Quasi-3D Analytical Engine (Document 19).

---

## 1. Why Coreless AFPM Needs Special Modeling

In coreless (ironless stator) AFPM machines:

- There is **no stator reluctance network** in the traditional sense.
- The effective air-gap is significantly larger.
- The magnetic field from the permanent magnets must be calculated using **analytical field solutions** rather than simple reluctance methods.
- Winding eddy current losses become more prominent because the conductors are directly exposed to the alternating PM field.
- Cogging torque is inherently very low or zero.

This requires a different modeling approach compared to slotted machines.

---

## 2. Recommended Analytical Approaches for Coreless AFPM

Based on recent high-quality literature (especially 2024–2025), the best approaches are:

### 2.1 Hague’s Analytical Solution + Multi-Slice Quasi-3D

- Use **Hague’s method** (or similar current sheet / permanent magnet analytical solutions) to calculate the air-gap magnetic field at multiple radial planes.
- This captures radial variation without requiring full 3D FEA.
- Particularly effective for single-stator double-rotor (SSDR) coreless configurations.

### 2.2 Fourier-Bessel Series Expansion

- Recent work (Rezaee-Alam 2025) shows strong results using **Fourier-Bessel series** for 3D analytical modeling of coreless stator AFPM.
- Good for handling edge effects and different PM shapes.
- More computationally intensive than simple Hague but still much faster than 3D FEA.

### 2.3 Hybrid MEC + Analytical (for partial coreless or hybrid topologies)

- Some designs use a combination of reluctance network in limited iron parts (if any) with analytical air-gap models.

**Recommendation for NeuroFlux Engine:**
Start with **Hague’s method + multi-slice quasi-3D** for speed, and add Fourier-Bessel support later for higher accuracy on complex coreless designs.

---

## 3. Key Equations for Coreless AFPM (Grounded)

### 3.1 Air-Gap Flux Density

For coreless machines, the radial and axial components of the magnetic field produced by surface-mounted PMs can be calculated analytically. A common approach uses the solution for the magnetic field of a permanent magnet in free space or between two rotors.

Typical form (simplified at mean radius):

\[
B_r(r, \theta, z), \quad B_z(r, \theta, z)
\]

These are derived from the magnetic scalar potential satisfying Laplace’s equation with appropriate boundary conditions from the PM magnetization.

### 3.2 Torque Production

Torque is still calculated from the interaction between the air-gap field and the stator currents, but the field distribution is smoother and the effective \( B_g \) is lower due to the large air-gap.

Simplified multi-slice torque contribution per plane:

\[
dT = r \cdot (B_z \cdot J_\theta) \cdot r \, dr \, d\theta \, dz
\]

Integrated across planes and azimuth.

### 3.3 Winding Eddy Current Losses (Critical in Coreless)

Because there is no stator iron to shield the windings, conductors experience significant alternating fields from the PMs.

Loss calculation often uses:

- Analytical expressions for eddy currents in rectangular or round conductors exposed to a known alternating field.
- Or 2D/3D FEA on the winding region only (hybrid approach).

Special winding techniques (Litz wire, thin conductors, transposed coils) are commonly used to mitigate these losses.

---

## 4. Implementation Considerations for the Python Engine

When extending the `Quasi3DAnalyticalEngine` (Document 19) to support coreless:

1. **Plane Generation**: Same radial slicing logic.
2. **Magnetic Field Calculation per Plane**:
   - Replace or condition the MEC solver with an analytical field calculator (Hague or Fourier-Bessel).
3. **Current Sheet / Winding Model**:
   - Model the stator winding as a current sheet or discrete conductors in the large air-gap.
4. **Loss Models**:
   - Emphasize PM-induced eddy currents in windings.
   - Copper losses remain important.
5. **No Saturation in Stator**: Simplifies the model significantly (no iterative saturation in iron parts).

---

## 5. Validation Strategy

For coreless models, recommended validation path:

- Compare against published analytical results (e.g., Rezaee-Alam 2025).
- Cross-check with 3D FEA on a few reference designs.
- Use symmetry-based ultra-fast FEA methods (2024 papers) for efficient validation.

---

## 6. Recommended Development Sequence for Coreless Support

1. Implement basic Hague-based air-gap field calculator for SSDR coreless at mean radius.
2. Extend to multiple radial planes (quasi-3D).
3. Add winding eddy loss model.
4. Integrate into the main `evaluate()` method with topology dispatch.
5. Add support for Halbach arrays (common and beneficial in coreless designs).
6. Add Fourier-Bessel option for higher accuracy.

---

## 7. Synergy with Digital Twin & Standards

Coreless AFPM digital twins can be particularly powerful because:
- Lower core losses → simpler thermal models.
- Very low cogging → excellent for smooth direct-drive applications.
- The analytical models developed here can directly feed into reduced-order models for real-time digital twin execution.

When exposing via AAS or ISO 23247 interfaces, coreless machines can have dedicated submodels for "Winding Eddy Loss Characteristics" and "Large Air-gap Field Distribution".

---

**This document provides the modeling foundation needed to extend the NeuroFlux analytical engine to coreless AFPM topologies.**

It builds directly on the Python structure defined in Document 19 and the mathematical grounding in Document 12.

**End of Coreless AFPM Analytical Modeling v1.0**