# REQUIREMENT RECONSTRUCTION
## Reconstructing the Challenge from First Principles

**Challenge Statement:** "Discover patentable AFPM aerospace starter-generator"  
**Analysis Date:** May 31, 2026  
**Status:** Requirements reconstructed from evidence

---

## PART 1: CHALLENGE STATEMENT DECONSTRUCTION

### Original Mission (from discovery_runner.py line 4)
```
"Discover patentable AFPM aerospace starter-generator"
```

### Key Terms Analysis

| Term | Interpretation | Evidence Required |
|------|----------------|-------------------|
| **Patentable** | Novel, non-obvious, useful; freedom to operate | Prior art search |
| **AFPM** | Axial Flux Permanent Magnet topology | Topology novelty |
| **Aerospace** | Aircraft application (DO-160 certified) | Certification path |
| **Starter-Generator** | Dual-mode: starts engine, generates power | Dual-mode validation |

### Fitness Function Weights (Evidence of Priority)

| Criterion | Weight | Inferred Priority |
|-----------|--------|-------------------|
| Power Density | 30% | **PRIMARY** |
| Thermal Margin | 20% | High (aerospace cooling limited) |
| Fault Tolerance | 15% | Medium (modular architecture) |
| Manufacturability | 15% | Medium (aerospace production) |
| Magnet Reduction | 10% | Lower (cost/rare-earth concern) |
| Certification | 10% | Entry requirement |

### Operating Point (Evidence from Code)

```python
OperatingPoint(speed_rpm=1800, I_rms=15.0)
```

- **Speed:** 1800 RPM (low-speed, direct-drive)
- **Implication:** Not high-speed aerospace (turbine-direct), likely APU or ground power

---

## PART 2: AEROSPACE APPLICATION MAP

### Application Classes

| Application | Power Range (kW) | RPM Range | Mass Range (kg) | Power Density Target | Reliability Target |
|-------------|------------------|-----------|-----------------|---------------------|-------------------|
| **UAV (Small)** | 0.5 - 5 | 3000-8000 | 0.5 - 5 | 1-3 kW/kg | >1000 hrs MTBF |
| **UAV (Large)** | 5 - 50 | 2000-6000 | 5 - 50 | 2-5 kW/kg | >2000 hrs MTBF |
| **eVTOL (Distributed)** | 50 - 300 per motor | 1500-4000 | 20 - 100 | 3-8 kW/kg | >3000 hrs MTBF |
| **APU (Auxiliary)** | 50 - 200 | 12000-24000 | 50 - 200 | 1-3 kW/kg | >8000 hrs MTBF |
| **Starter-Generator (Small)** | 5 - 50 | 6000-12000 | 10 - 50 | 1-3 kW/kg | >5000 hrs MTBF |
| **Starter-Generator (Large)** | 50 - 300 | 4000-10000 | 50 - 300 | 2-5 kW/kg | >10000 hrs MTBF |
| **Distributed Propulsion** | 100 - 500 per nacelle | 2000-5000 | 100 - 500 | 3-8 kW/kg | >15000 hrs MTBF |
| **Hybrid-Electric** | 100 - 1000 | 3000-8000 | 100 - 500 | 2-5 kW/kg | >12000 hrs MTBF |
| **Ground Power Unit** | 50 - 500 | 1800 (fixed) | 100 - 1000 | 0.5-2 kW/kg | >5000 hrs MTBF |
| **Demonstrator System** | 1 - 50 | Variable | Variable | Learning-focused | N/A |

### Target Application Identification

Given challenge constraints:
- **1800 RPM** → Low-speed, direct-drive, or APU/Ground Power
- **Starter-Generator** → Must start engine + generate power
- **Patentable** → Novelty required
- **Modular fault tolerance** → Likely safety-critical application

**Most Likely Applications (ranked by fit):**

1. **Ground Power Unit (GPU)** - Fixed 1800 RPM (60 Hz), starter-generator for aircraft on ground
2. **APU Starter-Generator** - Starts APU, generates power when engines off
3. **Small Aircraft Starter-Generator** - General aviation, business jets
4. **eVTOL Range Extender** - Lower RPM for noise/cogging, high reliability
5. **Demonstrator/Research** - Proof-of-concept for novel modular concept

---

## PART 3: AEROSPACE TRENDS & LITERATURE SYNTHESIS

### AFPM Literature Evidence

| Source Type | Key Finding | Relevance |
|-------------|-------------|-----------|
| Research Papers | AFPM achieves 1-5 kW/kg in 10-100 kW range | Power density target benchmark |
| Research Papers | Coreless AFPM: 93-97% efficiency, lower cogging | Efficiency/cogging tradeoff |
| Research Papers | Modular/stator-segmented: fault tolerance studied | Novelty depends on implementation |
| Aerospace Industry | Honeywell 1MW: 8 kW/kg, 97% efficiency | Upper bound benchmark |
| Aerospace Industry | Traditional starter-generators: 1-3 kW/kg | Competitive target |

### Low-Speed Generator Literature

| Speed Range | Typical Application | AFPM Advantage |
|-------------|-------------------|----------------|
| 100-500 RPM | Wind turbines | High torque density |
| 500-2000 RPM | Diesel generators | Compact vs radial |
| 1800 RPM | 60 Hz fixed frequency | Synchronous direct-drive |
| 3600 RPM | High-speed industrial | Pancake form factor |

### Starter-Generator Literature

| Aircraft Class | Starter Power (kW) | Generator Power (kW) | Speed (RPM) | Key Requirement |
|----------------|-------------------|----------------------|-------------|-----------------|
| General Aviation | 5 - 15 | 5 - 15 | 2000-2700 | Light weight |
| Business Jet | 20 - 50 | 20 - 50 | Variable | Dual-mode efficiency |
| Commercial Jet | 50 - 200 | 50 - 200 | Variable | High reliability |
| Helicopter | 30 - 100 | 30 - 100 | Variable | Compact, rugged |

### More-Electric Aircraft (MEA) Trends

| Trend | Impact on Generators | Requirement |
|-------|---------------------|-------------|
| Bleedless systems | More electrical power needed | Higher kW capacity |
| Distributed power | Multiple smaller generators | Modular, fault-tolerant |
| Electric actuation | Variable loads | Fast transient response |
| Weight reduction | Every kg matters | >3 kW/kg target |
| Reliability | No in-flight maintenance | >99.9% availability |

---

## PART 4: FEASIBILITY ENVELOPE CONSTRUCTION

### Power Envelope

| Boundary | Value | Rationale |
|----------|-------|-----------|
| **Minimum Useful** | 5 kW | Below this, not aircraft-relevant (too small for starter) |
| **Sweet Spot** | 20 - 100 kW | Starter-generator range for GA to business jets |
| **Maximum Useful** | 300 kW | Above this, different technology (turbine-direct) |
| **Likely Target** | 30 - 90 kW | Fits starter-generator mission, patentable niche |

### RPM Envelope

| Boundary | Value | Rationale |
|----------|-------|-----------|
| **Minimum** | 1500 RPM | Lower → massive diameter, impractical |
| **Sweet Spot** | 1800 - 3600 RPM | Synchronous speeds (60 Hz), direct-drive |
| **Maximum** | 6000 RPM | Structural limits, noise, bearings |
| **Likely Target** | 1800 RPM | Challenge code uses this; GPU/APU typical |

### Mass Envelope

| Boundary | Value | Rationale |
|----------|-------|-----------|
| **Minimum** | 5 kg | Below this, negligible contribution |
| **Sweet Spot** | 15 - 50 kg | Achievable with AFPM topology |
| **Maximum** | 150 kg | Above this, transportability issues |
| **Likely Target** | 20 - 40 kg | For 30-90 kW at 2-4 kW/kg |

### Power Density Envelope

| Boundary | Value | Rationale |
|----------|-------|-----------|
| **Minimum Competitive** | 1 kW/kg | Below this, not aerospace-competitive |
| **Sweet Spot** | 2 - 4 kW/kg | Achievable with AFPM, competitive |
| **Stretch Target** | 5 - 8 kW/kg | Honeywell territory, requires innovation |
| **Likely Target** | 2 - 3 kW/kg | For 30-90 kW, realistic with AFPM |

### Efficiency Envelope

| Boundary | Value | Rationale |
|----------|-------|-----------|
| **Minimum** | 90% | Below this, thermal issues |
| **Sweet Spot** | 94 - 96% | Achievable, competitive |
| **Stretch Target** | 97 - 98% | Honeywell/coreless territory |
| **Likely Target** | 94 - 96% | For starter-generator duty cycle |

---

## PART 5: FEASIBILITY ENVELOPE SUMMARY

### Most Likely Target Specifications

| Parameter | Likely Target | Range |
|-----------|---------------|-------|
| **Application** | Ground Power Unit / APU Starter-Gen | Or small aircraft starter-gen |
| **Power** | 30 - 90 kW | 20 - 100 kW envelope |
| **RPM** | 1800 | 1500 - 3600 range |
| **Mass** | 15 - 40 kg | For 2-4 kW/kg target |
| **Power Density** | 2 - 4 kW/kg | 1-5 kW/kg envelope |
| **Efficiency** | 94 - 96% | 90-98% envelope |
| **Fault Tolerance** | 50-80% degraded power | Modular architecture |
| **Patentability** | Novel modular topology | Freedom to operate required |

### Architecture Feasibility by Power Class

| Power Class | Relevance | Current Search Space Fit |
|-------------|-----------|-------------------------|
| **2 - 6 kW** | LOW | Too small for meaningful aerospace starter-gen |
| **20 - 50 kW** | HIGH | **OPTIMAL** - GA aircraft, small starter-gen |
| **50 - 200 kW** | HIGH | Good - business jets, APU, GPU |
| **200 - 1000 kW** | MEDIUM | Possible, but different technology likely |

### Search Space Assessment

**Current Search Space:** 2.6 - 3.6 kW (from discovery results)

| Aspect | Current | Required | Assessment |
|--------|---------|----------|------------|
| Power | 2-4 kW | 30-90 kW | **15-30× TOO SMALL** |
| Diameter | 0.15-0.30 m | 0.30-0.60 m | **Too small** |
| Speed | 1800 RPM | 1800 RPM | Correct |
| Topology | AFPM | AFPM | Correct |

**Verdict: Current search space is 15-30× too small for likely aerospace application.**

---

## PART 6: RECONSTRUCTED REQUIREMENTS

### Primary Requirements (Must Have)

| ID | Requirement | Target | Rationale |
|----|-------------|--------|-----------|
| R1 | Power Output | 30 - 90 kW | Starter-generator for GA to business jets |
| R2 | Power Density | >2 kW/kg | Aerospace competitive threshold |
| R3 | Efficiency | >94% | Thermal management in aircraft |
| R4 | Dual-Mode | Starter + Generator | Core mission requirement |
| R5 | Novelty | Patentable claim | Challenge requirement |
| R6 | Reliability | >5000 hrs MTBF | Aerospace starter-gen typical |

### Secondary Requirements (Should Have)

| ID | Requirement | Target | Rationale |
|----|-------------|--------|-----------|
| R7 | Fault Tolerance | Degraded operation | Modular value proposition |
| R8 | RPM Range | 1800 nominal | 60 Hz fixed frequency for GPU |
| R9 | Mass | <50 kg | Aircraft weight budget |
| R10 | Certification Path | DO-160 | Aerospace compliance |

### Tertiary Requirements (Nice to Have)

| ID | Requirement | Target | Rationale |
|----|-------------|--------|-----------|
| R11 | Magnet Reduction | >20% less NdFeB | Cost/rare-earth sustainability |
| R12 | Manufacturability | Standard processes | Cost control |
| R13 | Thermal Margin | >30°C | Safety margin |

---

## PART 7: RECONSTRUCTED VALIDATION STRATEGY

### Kill-Switch Tests (Do First)

| Test | Purpose | Trigger |
|------|---------|---------|
| **K1: Prior Art Search** | Patentability | If strong prior art: TERMINATE |
| **K2: Power Scaling** | Feasibility at 30-90 kW | If analytical model fails: TERMINATE |
| **K3: Mass Reality Check** | Power density achievable | If >5 kg/kW: Architecture invalid |

### Core Validation (Required)

| Test | Purpose | Evidence |
|------|---------|----------|
| V1: Analytical at 30-90 kW | Feasibility | Power, efficiency, mass |
| V2: 2D FEM validation | Field accuracy | Flux, losses, inductance |
| V3: Thermal modeling | Cooling adequacy | Temp rise at rated power |
| V4: Starter-mode validation | Torque capability | Starting torque, transient |
| V5: Fault tolerance circuit | Degraded operation | Simulation of failures |

### Optional Validation (Defer)

| Test | Purpose | When |
|------|---------|------|
| X1: 3D FEM | End effects | If 2D shows anomalies |
| X2: Hardware prototype | Real validation | If analytical/FEM promising |
| X3: Certification testing | DO-160 | If moving to production |

---

## PART 8: FINAL ANSWERS

### 1. Most Likely Application

**Ground Power Unit (GPU) or APU Starter-Generator**

**Evidence:**
- 1800 RPM matches 60 Hz fixed frequency for ground power
- 30-90 kW matches GPU power requirements
- Dual-mode (starter-generator) matches APU needs
- Modular fault tolerance valuable for ground support equipment

### 2. Most Likely Power Range

**30 - 90 kW**

**Evidence:**
- Below 30 kW: Not useful as starter for most aircraft
- Above 90 kW: Different technology (turbine-direct) usually preferred
- Sweet spot: GA aircraft (5-15 kW), business jets (20-50 kW), small APU (50-100 kW)
- Challenge weights: Power density 30% suggests power is primary metric

### 3. Most Likely RPM Range

**1800 RPM (nominal), 1500-3600 RPM (range)**

**Evidence:**
- Challenge code explicitly uses 1800 RPM
- 1800 RPM = 60 Hz synchronous (4-pole) for ground power
- 3600 RPM = 60 Hz synchronous (2-pole) for higher power density
- Low-speed reduces noise, cogging (important for GPU near aircraft)

### 4. Most Likely Success Metric

**Power Density >2 kW/kg at 30-90 kW with >94% efficiency and patentable novelty**

**Evidence:**
- Fitness function: Power density weighted 30% (highest)
- Aerospace trend: Weight reduction critical
- Honeywell benchmark: 8 kW/kg (upper bound)
- Traditional starter-gen: 1-3 kW/kg (competitive target)
- Patentable novelty: Core challenge requirement

### 5. Is Current Search Space Appropriate?

**NO. Current search space is 15-30× TOO SMALL.**

**Current:** 2.6 - 3.6 kW  
**Required:** 30 - 90 kW  
**Gap:** 15-30×

**Implication:** Validating 3 kW machines tells us nothing about 30-90 kW aerospace starter-generator feasibility. Scaling laws are non-linear (thermal, structural, manufacturing all change).

### 6. Should Project Scale Up, Pivot, or Continue?

**SCALE UP.**

**Rationale:**

| Option | Assessment |
|--------|------------|
| **Continue (2-6 kW)** | ❌ No aerospace value at this power level |
| **Pivot (different tech)** | ⚠️ AFPM is correct technology, wrong scale |
| **Scale Up (30-90 kW)** | ✅ Correct path to meet challenge requirements |

**Recommended Action:**

1. **Immediate:** Re-parameterize search space for 30-90 kW
   - D_out: 0.30 - 0.60 m (vs current 0.15-0.35 m)
   - Current density: Same
   - Speed: 1800 RPM (keep)
   
2. **First:** Analytical validation at 30-90 kW
   - Does AFPM topology achieve 2-4 kW/kg at this scale?
   - Does modular fault tolerance concept scale?
   
3. **Then:** FEM validation if analytical promising
   
4. **Kill condition:** If 30-90 kW analytically infeasible with AFPM

---

## CONCLUSION

### What We Learned

1. **Challenge is NOT about beating Honeywell 1 MW** - Wrong comparison
2. **Challenge is about 30-90 kW aerospace starter-generator** - Right target
3. **Current search space is 15-30× too small** - Fundamental mismatch
4. **AFPM topology is appropriate** - Just wrong scale
5. **Modular fault tolerance may be patentable** - Novelty potential exists

### The Path Forward

**SCALE UP to 30-90 kW.**

The current 2-6 kW validation effort is solving a problem that doesn't exist. The aerospace need is for 30-90 kW starter-generators with 2-4 kW/kg power density.

**Do not validate 3 kW machines.**  
**Validate 30-90 kW feasibility.**  
**Then optimize within that envelope.**

---

**END OF REQUIREMENT RECONSTRUCTION**
