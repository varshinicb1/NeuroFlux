# AFPM Mathematical Foundation and Equation Reference
## Grounding Document for AI Agents — Strict Source-Based Equations Only

**Purpose:** This document compiles **all key mathematical equations** from foundational and recent literature on Axial-Flux Permanent Magnet (AFPM) machines. It is designed to ground AI agents so they **never hallucinate or invent equations**. Every equation must be traceable to a cited source.

**Date:** May 30, 2026  
**Primary Sources:**
- Parviainen (2005) PhD Thesis (most detailed low-speed AFPM analytical model)
- Hemeida et al. (2019) Quasi-3D MEC
- Gieras et al. books and papers
- Huang, Campbell, Chan, and recent reviews (2022–2025)
- Selected high-quality papers on coreless/YASA topologies

**Rule for AI Agents:** When using any equation from this document, you **must** cite the source section. If an equation is not here, do not invent it — request clarification or further research.

---

## 1. General Torque Production and Sizing Equations

### 1.1 Idealized Double-Sided AFPM Torque (Campbell 1974, Parviainen 2005)

For an idealized axial-flux machine with square-wave flux density `B_max` and linear current density `A`:

\[
dT_{em} = 2\pi r \cdot A_{in} \cdot B_{max} \cdot r \, dr
\]

Integrated over radius:

\[
T_{em} = \frac{\pi}{2} B_{max} A_{in} (r_{out}^3 - r_{in}^3) = \frac{\pi}{2} B_{max} A_{in} r_{out}^3 (1 - k_D^3)
\]

Where diameter ratio:

\[
k_D = \frac{r_{in}}{r_{out}}
\]

**Optimal diameter ratio** (for idealized case):

\[
k_{D,opt} \approx 0.58 \quad \text{(from } \frac{dT}{dk_D} = 0\text{)}
\]

**Practical range:** \( 0.6 \leq k_D \leq 0.7 \)

**Source:** Parviainen (2005), Chapter 1.3.1; Campbell (1974)

### 1.2 General Sizing Equation (Gieras / Huang style)

For AFPM:

\[
T = \frac{\pi}{4} k_D (1 - k_D^2) B_g A D_o^3 \cdot \eta \cdot \cos\phi \quad \text{(approx)}
\]

More precise forms appear in Gieras "Axial Flux Permanent Magnet Brushless Machines".

---

## 2. Magnetic Circuit and Air-Gap Flux Density

### 2.1 Parviainen Quasi-3D Approach (2005)

Machine is divided into `N` computation planes. For plane `i`:

Average diameter of plane `i`:

\[
D_{ave,i} = D_{out} - \frac{2i-1}{N} l_s
\]

Pole pitch at plane `i`:

\[
\tau_{p,i} = \frac{\pi D_{ave,i}}{2p}
\]

Relative magnet width (can vary with radius):

\[
\alpha_{p,i} = \frac{w_{PM,i}}{\tau_{p,i}}
\]

### 2.2 Magnetic Equivalent Circuit (Reluctance Network)

Flux:

\[
\Phi = \Re^{-1} F
\]

Reluctance of element `i`:

\[
\Re_i = \frac{l_i}{\mu_0 \mu_r S_i}
\]

MMF from PM:

\[
F_{PM} = \frac{B_r l_{PM}}{\mu_0 \mu_{r,PM}}
\]

Saturation factor (iterative):

\[
k_{sat} = \frac{\Theta_{agap} + \Theta_t + \Theta_y + \Theta_{rotor}}{0.5 \Theta_{agap}}
\]

Effective air-gap:

\[
g_{eff} = k_{sat} k_C g
\]

**Source:** Parviainen (2005), Chapter 2.2.1

### 2.3 Hemeida 2019 Quasi-3D MEC Improvements

Hemeida et al. (2019) present a **simplified and more efficient** quasi-3D MEC specifically for surface-mounted AFPM. The model reduces the number of reluctances while maintaining good accuracy for radial variation and saturation. It is currently one of the best practical implementations for fast analytical engines.

**Key feature:** Better handling of radial dependence of flux density and saturation with lower computational cost than earlier networks.

---

## 3. Loss Models

### 3.1 Copper Losses

\[
P_{Cu} = m I_{ph}^2 R_{ph}
\]

End-winding and slot copper are calculated separately in detailed models (important for AFPM due to long end-windings).

### 3.2 Iron Losses (Bertotti / Steinmetz based)

Common form used in Parviainen:

\[
P_{Fe} = k_{hys} f B^\alpha + k_{eddy} (f B)^2 + k_{exc} (f B)^{1.5}
\]

Parviainen uses specific coefficients for M600-50A steel.

### 3.3 Permanent Magnet Eddy Current Losses

Significant in AFPM due to slot harmonics and PWM. Calculated per computation plane in quasi-3D models.

---

## 4. Inductances

### 4.1 d-q Axis Inductances (Parviainen)

Calculated using the reluctance network on d-axis and q-axis separately.

Main difference comes from saturation on d-axis due to PM flux.

Typical result: \( L_d \approx L_q \) or slightly lower for surface-mounted designs (because PM acts like air).

---

## 5. Thermal Modeling (Parviainen 2005)

Parviainen developed a **thermal resistance network** integrated into the iterative design procedure.

Main heat paths:
- Conduction through stator yoke and teeth
- Convection in air-gap (uses Nusselt, Reynolds, Taylor numbers)
- Radiation
- Water cooling options

Key parameters: heat transfer coefficient `h`, thermal resistance network for main paths.

---

## 6. Mechanical Constraints

### 6.1 Rotor Disk Deflection (Parviainen Appendix A.2)

For rotor support structure, maximum deflection `y_def` under uniform magnetic pressure.

Two common support structures analyzed with equations involving:
- Modulus of elasticity `Γ`
- Poisson’s ratio `υ`
- Rotor thickness `l_rotor`
- Support radius `r_sup`

### 6.2 Stator Natural Frequency

For AFPM stator (annular disk approximation):

\[
f_n = \frac{k_n}{2\pi r_{s,out}} \sqrt{\frac{\Gamma l_y^2}{12(1 - \upsilon^2) \rho}}
\]

Mode coefficient `k_n` depends on diameter ratio `k_D`.

**Source:** Parviainen Appendix A.1 (based on Leissa and Yang)

---

## 7. AF vs RF Comparison Framework (Parviainen Chapter 5)

Parviainen performs one of the most rigorous comparisons using:
- Same electrical loading `A`
- Same magnetic loading `B_g`
- Same current density `J`
- Mechanical constraints applied to both topologies

Key findings (with equations):
- Volume ratio `V_AF / V_RF` strongly depends on RF length ratio `k_l = l / D_agap`
- AF advantage appears clearly when `k_l < 0.5`
- Efficiency of AF is generally slightly lower due to longer end-windings (more copper)
- Cost comparison includes active material + total steel consumption (scrap factor higher for RF)

---

## 8. Coreless and YASA Specific Equations

Coreless AFPM:
- No stator iron → very low core losses
- Larger effective air-gap → lower flux density
- Torque still follows similar form but with different `B_g` and higher copper losses possible
- Recent 2025 papers provide analytical models using Hague’s solution + Fourier-Bessel series for coreless stators.

YASA (Yokeless and Segmented Armature):
- Segmented stator teeth → reduced iron losses + better cooling
- Flux paths more 3D → quasi-3D or full 3D models preferred

---

## 9. Summary Table of Critical Equations

| Category                    | Key Equation Type                          | Primary Source          | Notes / Limitations                     |
|----------------------------|--------------------------------------------|-------------------------|-----------------------------------------|
| Torque (Ideal)             | \( T \propto B A (r_{out}^3 - r_{in}^3) \) | Campbell / Parviainen   | Idealized square wave                   |
| Quasi-3D Geometry          | Multiple planes + unrolling                | Parviainen 2005         | Captures radial variation               |
| MEC Reluctance             | \( \Re = l / (\mu_0 \mu_r S) \)            | Parviainen + Hemeida    | Iterative saturation                    |
| Saturation Factor          | \( k_{sat} \)                              | Parviainen              | Adjusts effective air-gap               |
| Iron Losses                | Bertotti / Steinmetz form                  | Parviainen              | Material-specific coefficients          |
| Rotor Deflection           | Analytical disk formulas                   | Parviainen Appendix     | Two support structure cases             |
| Natural Frequency          | Annular disk vibration modes               | Parviainen Appendix     | Critical for large diameter stators     |
| AF vs RF Volume            | \( V_{rel} = V_{AF} / V_{RF}(k_l) \)       | Parviainen Ch. 5        | Strong function of `k_l`                |

---

## 10. Instructions for Grounded AI Agents

1. **Never invent equations.** Only use equations explicitly listed in this document or request addition of new sourced equations.
2. When answering, **always cite the section** (e.g., "Using Parviainen 2005 Eq. for torque...").
3. For any new topology or advanced feature not covered here, flag it and suggest literature search first.
4. Prefer **quasi-3D MEC** (Hemeida 2019 style) for fast analytical engines.
5. For final validation, always recommend 2D/3D FEA correlation.

---

**This document will be continuously expanded** as new high-quality sources are analyzed.

**Next planned additions:**
- Full set of Hemeida 2019 MEC equations (when detailed extraction is complete)
- Coreless analytical models (Rezaee-Alam 2025 style)
- More recent ML-surrogate + analytical hybrid methods

---

**End of Grounding Document v1.0**