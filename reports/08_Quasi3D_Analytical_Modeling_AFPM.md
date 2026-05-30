# Quasi-3D Analytical Modeling Techniques for Axial-Flux Permanent Magnet Machines

**Focus:** AFPM (especially surface-mounted, low-speed, one-rotor-two-stators topology)  
**Relevance to NeuroFlux:** Excellent foundation for a fast, accurate **Analytical Simulation Engine** that can be used in optimization loops and preliminary design.

**Date:** May 30, 2026

---

## 1. Why Quasi-3D Modeling?

Axial-Flux Permanent Magnet (AFPM) machines have an **inherently 3D geometry**:
- Magnetic flux flows mainly in the **axial** direction.
- Geometry and magnetic quantities (pole pitch, flux density, saturation) **vary significantly with radius**.
- Complex magnet shapes and slotting create 3D effects.

**Full 3D Finite Element Analysis (FEA)** is accurate but extremely slow — unsuitable for iterative design, optimization, or real-time engine use in NeuroFlux.

**Quasi-3D (or "multi-slice 2D") modeling** offers a powerful compromise:
- It approximates the 3D problem by slicing the machine radially into several thin 2D problems.
- Each slice is solved independently (analytically or with Magnetic Equivalent Circuit).
- Results are combined to reconstruct overall machine behavior.

This approach captures the **radial variation** that simple average-radius 2D models miss, while remaining computationally efficient.

---

## 2. Core Principle of Quasi-3D Approach

The machine is divided radially into **N thin cylindrical slices** (computation planes), each of small radial thickness `dr`.

For each slice `i` at average radius `r_i`:
1. "Unroll" the cylindrical slice into a linear (Cartesian) 2D model.
2. Solve the 2D electromagnetic problem for that slice.
3. Calculate local quantities: flux density, back-EMF contribution, losses, torque contribution, etc.
4. Integrate/sum across all slices to get global performance.

**Key benefit**: Different slices have different pole pitch `τ_p,i`, different magnet width relative to pole pitch, and different saturation levels. This is critical for accurate design, especially when magnet shape is complex or when inner/outer radius effects are strong.

---

## 3. Foundational Work: Parviainen (2005)

Asko Parviainen’s PhD thesis is one of the most important references for quasi-3D AFPM modeling.

**Main contributions**:
- Systematic quasi-3D analytical design procedure for surface-mounted AFPM (one-rotor-two-stators).
- Uses **non-linear Magnetic Equivalent Circuit (MEC / reluctance network)** per computation plane.
- Iterative solution to account for saturation.
- Includes calculation of:
  - Air-gap flux density distribution
  - Back-EMF
  - Inductances (d-q axis)
  - Cogging torque
  - Iron losses, copper losses, PM eddy current losses
  - Thermal model integration
- Validated against prototype measurements.

**Strengths**:
- Practical for preliminary design.
- Combines electromagnetic + thermal modeling.
- Handles complex magnet shapes better than single-plane models.

**Limitations** (addressed in later work):
- Relatively coarse reluctance network.
- Computational cost grows with number of slices.
- Some 3D effects (radial flux flow between slices) are neglected.

---

## 4. Modern Improvement: Hemeida et al. (2019)

**Paper**: *"A Simple and Efficient Quasi-3D Magnetic Equivalent Circuit for Surface Axial Flux Permanent Magnet Synchronous Machines"*  
IEEE Transactions on Industrial Electronics, 2019 (highly cited).

**Key advances over earlier methods**:
- More efficient and simplified MEC formulation specifically tailored for surface-mounted AFPM.
- Better balance between accuracy and computational speed.
- Improved handling of radial variation and saturation.
- Designed to be practical for design optimization loops.

This paper is currently one of the best references for implementing a **fast quasi-3D engine** in NeuroFlux.

---

## 5. Other Notable Quasi-3D Techniques

| Technique | Description | Strengths | Typical Use |
|-----------|-------------|-----------|-------------|
| **MEC / Reluctance Network** (Parviainen, Hemeida) | Nonlinear reluctance model per slice | Fast, handles saturation well | Preliminary design + optimization |
| **Analytical (Hague’s solution + Fourier)** | Closed-form solution of Maxwell equations per slice | Very fast for air-gap field | Air-gap flux density focused studies |
| **Hybrid MEC + Analytical** | MEC for iron parts + analytical for air-gap | Good accuracy/speed trade-off | Modern implementations |
| **Fourier-Bessel series** (recent coreless AFPM) | Advanced analytical expansion | High accuracy for coreless topologies | Specialized coreless AFPM |

A 2025 paper on coreless stator AFPM compares several of these analytical quasi-3D techniques.

---

## 6. Advantages and Limitations

**Advantages**:
- **Speed**: Orders of magnitude faster than 3D FEA.
- **Radial variation**: Captures inner vs outer radius differences.
- **Good for optimization**: Can be embedded in genetic algorithms, gradient methods, or ML surrogate training loops.
- **Physical insight**: Easier to understand and debug than black-box FEA.

**Limitations**:
- Assumes **no significant radial flux flow** between adjacent slices (main approximation).
- Accuracy decreases in highly saturated designs or when strong 3D end-effects/leakage is dominant.
- Requires careful choice of number of slices (`N`) and slice thickness.
- Less accurate than full 3D FEA for final verification (should be validated with FEA or measurements).

---

## 7. Implementation Recommendations for NeuroFlux

For the **Analytical Simulation Engine**, the following architecture is recommended:

1. **Input**: Machine geometry parameters (inner/outer diameter, magnet shape, winding, materials, operating point).
2. **Quasi-3D Core**:
   - User-defined or adaptive number of radial slices.
   - Per-slice MEC solver (inspired by Hemeida 2019 + Parviainen).
   - Analytical air-gap field calculation option.
3. **Post-processing**:
   - Integrate torque, back-EMF, losses across slices.
   - Calculate efficiency, power factor, thermal estimates.
4. **Output**: Performance metrics + field distributions (per slice + global).
5. **Validation layer**: Compare against 2D/3D FEA on selected designs.

**Future Enhancements**:
- Couple with thermal network (as Parviainen did).
- Add surrogate/ML model trained on quasi-3D results for even faster evaluation.
- Extend to coreless/yokeless topologies.

---

## 8. Key References (Priority for NeuroFlux)

1. **Parviainen (2005)** – Foundational thesis. Read Chapters 2 and 5 in detail.
2. **Hemeida et al. (2019)** – Best modern quasi-3D MEC implementation. Highest priority for coding.
3. Recent coreless AFPM analytical papers (2025) – For extending to advanced topologies.
4. Abbaszadeh and others on quasi-3D with eccentricity/fault modeling.

---

**Conclusion**

Quasi-3D analytical modeling (especially MEC-based) is one of the most practical and powerful techniques for building a fast, physics-based simulation engine for AFPM machines. It directly addresses the 3D nature of axial-flux geometry without the computational burden of full 3D FEA.

This should be a **core component** of NeuroFlux’s multi-fidelity simulation stack (Analytical/Quasi-3D → 2D FEA → 3D FEA).

Would you like me to:
- Start drafting Python pseudocode / structure for a Quasi-3D MEC engine based on these methods?
- Deep-dive into the Hemeida 2019 paper equations?
- Compare quasi-3D accuracy vs full 3D FEA using available data? 

Let me know the next step.