# NeuroFlux Radical AFPM Concept: AEGIS-AFSG

## Concept Name

AEGIS-AFSG: Aerospace Electric Generator with Integrated Segmented Axial-Flux Switching.

## Core Invention

AEGIS-AFSG is not a conventional axial-flux permanent-magnet generator with magnets
spinning on a rotor disk. It is a low-speed aerospace generator that moves the
highest-risk components off the rotor:

- permanent magnets are held in liquid-cooled stator cassettes
- phase windings are physically isolated in replaceable stator sectors
- the rotor is a passive salient flux-modulation disk with no magnets
- each stator cassette has its own rectifier channel, temperature sensing, and bypass path
- a cold-plate/vapor-spreader ring removes heat directly from magnets and windings

The machine behaves like an axial-flux flux-switching / flux-modulated PM generator:
the passive rotor switches stator-mounted magnet flux through isolated armature
cassettes. This preserves low-speed torque density advantages while removing the
most serious aerospace certification objection: high-energy permanent magnets on
the rotating member.

## Why This Is Better Than A Normal AFPM

Normal AFPM machines are attractive because they are thin and torque dense, but the
aerospace objections are severe:

- rotor magnets can release under overspeed or bond failure
- rotor magnet heat is hard to remove
- permanent magnets create uncontrolled generation during converter faults
- tight axial gaps are vulnerable to rotor bow and bearing stack-up
- a monolithic stator winding is hard to isolate after a fault

AEGIS-AFSG changes the failure physics:

- magnet containment becomes a stationary structure problem
- magnet cooling becomes a direct cold-plate problem
- winding faults can be isolated cassette-by-cassette
- the rotor can be inspected as a passive metallic part
- degraded operation is possible with failed sectors disabled

## Architecture

| Subsystem | Design Choice | Rationale |
|---|---|---|
| Rotor | Passive salient axial flux-modulation disk | No rotor magnets; improves containment and overspeed safety |
| Stator | 12 to 18 removable phase-isolated cassettes | Enables fault isolation and maintainability |
| Magnets | Stator-mounted high-temperature PM or SmCo inserts | Easier thermal management and retention |
| Windings | Dual isolated three-phase or six-phase fractional-slot | Degraded operation after channel fault |
| Cooling | Dual-sided annular cold plate plus local vapor spreader | Direct heat extraction from stationary heat sources |
| Power electronics | Cassette-level rectification and health monitoring | Limits fault propagation |
| Sensing | RTD plus optional fiber Bragg strain/temperature sensors | Supports digital twin and certification evidence |
| Mechanical | Passive rotor with non-contact flux modulation | Reduces hidden magnet-retention risk |

## Mission Fit

Best fit:

- hybrid-electric turbogenerator accessory stage
- APU-integrated starter-generator demonstrator
- rotorcraft accessory generation
- high-reliability UAV generator
- hydrogen aircraft auxiliary generator using available cold sink

Not best fit:

- lowest-cost commodity wind generator
- ultra-high-speed starter-generator
- production flight hardware without substantial qualification testing

## Novelty Map

AEGIS-AFSG deliberately combines ideas that usually live in separate design families:

- axial-flux packaging
- flux-switching PM machine physics
- magnetic flux modulation / vernier behavior
- cassette-level aerospace fault isolation
- stationary magnet thermal management
- digital-twin health monitoring

The white space is not "axial flux" alone. The white space is:

> A stationary-magnet, cassette-isolated, liquid-cooled axial-flux switching
> generator for aerospace low-speed generation, with passive rotor containment
> and degraded-mode operation.

## Patentable Hypotheses

1. Stationary-magnet axial-flux switching generator with removable liquid-cooled
   phase cassettes.
2. Passive axial modulation rotor with integrated overspeed containment geometry.
3. Cassette-level health monitoring and bypass for degraded aircraft generation.
4. Vapor-spreader/cold-plate ring directly bonded to PM and winding modules.
5. Hybrid PM plus trim-field cassette for regulated voltage without rotor excitation.

## Review-Board Objections And Responses

| Objection | Response |
|---|---|
| Why not radial flux? | Radial flux has precedent, but lower torque density in pancake envelopes. AEGIS reduces AFPM-specific rotor magnet risk. |
| What fails first? | Thermal interface or cassette insulation. Both are stationary and inspectable. |
| What cannot be certified? | Flight certification cannot be claimed yet. The correct claim is TRL 3/4 demonstrator with DO-160/MIL-STD-704 validation path. |
| What is hidden risk? | Flux-switching ripple, acoustic signature, and local saturation. Requires 3D EM FEA before hardware. |
| What is the biggest challenge? | Achieving high specific power while keeping flux-switching losses and ripple acceptable. |

## Required Validation

HIGH CONFIDENCE:

- stationary magnet containment is mechanically easier than rotor magnet retention
- cassette-level isolation improves maintainability and fault containment
- thermal loads are easier to cool when PMs and windings are stationary

MEDIUM CONFIDENCE:

- axial flux-switching topology can meet low-speed generator torque requirements
- multiphase cassettes can support degraded operation
- cold plate plus vapor spreader can keep winding hotspots below limit

LOW CONFIDENCE:

- final electromagnetic performance without 3D EM FEA
- acoustic and torque ripple behavior
- final certification acceptance
- cost versus incumbent radial/wound-field systems

## Immediate NeuroFlux Work Items

1. Add AEGIS-AFSG as a new topology family in the candidate generator.
2. Build a 3D magnetic FEA handoff model: passive salient rotor, stator PM bridges,
   and phase cassette coils.
3. Reuse completed 3D thermal FEA, but move heat sources to stationary cassettes.
4. Generate a revised CAD package showing cassette sectors and passive rotor.
5. Add a presentation slide showing why "no rotor magnets" is the aerospace hook.

