# Coreless Axial-Flux Permanent Magnet (AFPM) Topologies — Deep Investigation

**Focus:** Coreless / Air-cored / Ironless Stator AFPM machines  
**Relevance to NeuroFlux:** High — offers very low core losses, lighter weight, simpler manufacturing in some cases, and excellent potential for high-efficiency or high-speed applications. Requires different analytical models than traditional slotted AFPM.

**Date:** May 30, 2026

---

## 1. What is a Coreless AFPM?

In a **coreless AFPM**, the stator has **no ferromagnetic material** (no teeth or yoke). The windings are placed directly in the air-gap, usually fixed in epoxy resin or a non-magnetic structure.

**Main variants:**
- Single-stator double-rotor (most common for coreless)
- Double-stator single-rotor
- Multi-stage / multi-disk coreless

**Key Characteristics:**
- Very low stator core losses (often near zero)
- Larger effective air-gap → lower air-gap flux density
- Reduced cogging torque (sometimes near zero)
- Higher copper losses possible (windings exposed to alternating PM field)
- Lighter stator, potentially better power-to-weight ratio
- Good thermal characteristics in some designs (windings directly cooled)

---

## 2. Advantages and Trade-offs

**Advantages:**
- Extremely low core losses → high efficiency at high frequencies/speeds
- No saturation in stator → linear behavior
- Simpler stator manufacturing (no lamination stacking in complex 3D shape)
- Low cogging torque → excellent for direct-drive
- Good for aerospace, small wind turbines, high-speed generators

**Trade-offs / Challenges:**
- Larger air-gap → lower flux density → more PM material often needed
- Windings experience higher eddy currents from PM field (need special winding techniques: Litz wire, thin conductors, or composite coils)
- Mechanical structure must hold windings rigidly against axial forces
- Lower power factor in some designs
- Thermal management of windings becomes critical

---

## 3. Key Topologies

### 3.1 Single-Stator Double-Rotor Coreless (SSDR Coreless)
- Most researched coreless configuration.
- Two PM rotors with coreless stator in between.
- Flux path goes axially through the stator winding region.
- Often uses **planar coils** or **concentrated windings** embedded in resin.

### 3.2 Multi-Stage Coreless
- Multiple coreless stators and rotors stacked.
- Increases power while keeping axial length manageable.
- Good for higher power direct-drive applications.

### 3.3 PCB Stator Coreless AFPM
- Stator windings printed on PCB.
- Very thin stator, excellent for integration.
- Popular in small high-speed or low-power applications.
- Manufacturing advantages (automated PCB process).

### 3.4 Halbach Array Rotor Coreless
- Halbach PM arrays on rotors to increase air-gap flux density and reduce back-iron thickness.
- Particularly effective in coreless designs because there is no stator iron to shape the field.

---

## 4. Analytical Modeling Approaches (Critical for NeuroFlux)

Coreless AFPM requires **different modeling** than slotted machines because there is no stator reluctance network in the traditional sense.

**Recent High-Quality Approaches (2024–2025):**

1. **Rezaee-Alam et al. (2025)** — *Analytical modeling of coreless stator axial flux PM machines*
   - Compares three techniques:
     - Quasi-3D analytical model
     - Magnetic Equivalent Circuit (MEC)
     - Analytical model based on **Fourier-Bessel series**
   - Excellent for no-load condition; considers edge and curvature effects + different PM shapes.

2. **Review papers on coreless AFPM for electric aircraft (2025)**
   - Focus on flux density equations with Halbach arrays.
   - Analytical torque and back-EMF at average diameter or multiple radial cuts.

3. **Ultra-fast FEA methods (2024)**
   - Exploit symmetry in coreless machines to drastically reduce number of FEA solutions needed.

**Recommended for NeuroFlux Engine:**
- Start with **Fourier-Bessel series + quasi-3D** for fast analytical coreless models.
- Use symmetry-based ultra-fast FEA for validation.

---

## 5. Key Equations Specific to Coreless AFPM

### 5.1 Air-Gap Flux Density
Because there is no stator iron, the air-gap is larger and the field from PMs is calculated differently (often using analytical solutions for current sheets or permanent magnets in free space).

Hague’s analytical solution is frequently used for the magnetic field of PMs in coreless machines.

### 5.2 Torque Production
Similar form to conventional AFPM, but with lower effective `B_g`:

\[
T \approx \frac{\pi}{2} B_g A r_m^2 (r_{out} - r_{in}) \quad \text{(simplified at mean radius)}
\]

More accurate multi-slice or 3D analytical models are preferred.

### 5.3 Winding Eddy Current Losses
Much more important in coreless designs because windings are directly exposed to the alternating PM field.

Special techniques:
- Litz wire
- Thin rectangular conductors
- Composite structure coils (recent papers propose novel coil designs to reduce eddy losses)

---

## 6. Manufacturing and Practical Considerations

- **Winding fixation**: Critical — windings must withstand axial magnetic forces and vibration.
- **Resin / encapsulation**: Must have good thermal conductivity and mechanical strength.
- **PM retention**: On rotors — often surface-mounted with protective cover or buried.
- **PCB stators**: Very promising for small-to-medium power; automated manufacturing.

---

## 7. Relevance to NeuroFlux Vision

Coreless AFPM is an excellent candidate for:
- High-efficiency low-speed generators (small wind, hydro)
- Aerospace / high power-to-weight applications
- Topologies where low cogging and smooth torque are critical

**Integration Opportunities:**
- Extend the Quasi-3D analytical engine to support coreless configurations (different air-gap model + winding loss model).
- Add coreless as a distinct topology class in the design space explorer.
- Use recent Fourier-Bessel analytical models as fast evaluation engines.

---

## 8. Recommended Next Steps for NeuroFlux

1. Extract detailed equations from Rezaee-Alam 2025 paper (Fourier-Bessel + quasi-3D for coreless).
2. Add coreless topology support to the mathematical foundation document.
3. Develop a dedicated **Coreless AFPM Analytical Engine** module.
4. Compare performance (efficiency, torque density, cost) of coreless vs slotted AFPM using the same loading conditions.

---

**This document will be expanded** with specific equations from the latest coreless papers.

**End of Coreless AFPM Investigation v1.0**