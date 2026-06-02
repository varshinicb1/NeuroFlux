# AFPM Aerospace Starter-Generator Discovery Report

## Mission Summary
- Evaluated: 100 candidate architectures
- Valid designs: 52 passed all constraints
- Top 10 selected by combined fitness + novelty

## Top 10 Architectures

### Rank 1: DSSR_SLOTTED

- **Combined Score**: 0.650
- **Fitness**: 0.628
- **Novelty Score**: 0.70 (HIGH)
- **Power**: 2.6 kW
- **Efficiency**: 98.5%
- **Geometry**: D=300mm, p=4, Q=12
- **Modularity**: 6 segments
- **Magnet Segments**: 4
- **Max Temperature**: 70.8C

#### Fault Tolerance Analysis

- 0 modules failed: 100% power available
- 1 modules failed: 83% power available
- 2 modules failed: 67% power available

### Rank 2: SSDR_CORELESS

- **Combined Score**: 0.647
- **Fitness**: 0.625
- **Novelty Score**: 0.70 (HIGH)
- **Power**: 3.6 kW
- **Efficiency**: 99.2%
- **Geometry**: D=150mm, p=4, Q=18
- **Modularity**: 6 segments
- **Magnet Segments**: 4
- **Max Temperature**: 70.6C

#### Fault Tolerance Analysis

- 0 modules failed: 100% power available
- 1 modules failed: 83% power available
- 2 modules failed: 67% power available

### Rank 3: DSSR_SLOTTED

- **Combined Score**: 0.643
- **Fitness**: 0.619
- **Novelty Score**: 0.70 (HIGH)
- **Power**: 1.6 kW
- **Efficiency**: 97.7%
- **Geometry**: D=150mm, p=4, Q=12
- **Modularity**: 6 segments
- **Magnet Segments**: 4
- **Max Temperature**: 70.8C

#### Fault Tolerance Analysis

- 0 modules failed: 100% power available
- 1 modules failed: 83% power available
- 2 modules failed: 67% power available

### Rank 4: SSDR_CORELESS

- **Combined Score**: 0.643
- **Fitness**: 0.619
- **Novelty Score**: 0.70 (HIGH)
- **Power**: 3.6 kW
- **Efficiency**: 99.2%
- **Geometry**: D=250mm, p=4, Q=6
- **Modularity**: 6 segments
- **Magnet Segments**: 4
- **Max Temperature**: 70.6C

#### Fault Tolerance Analysis

- 0 modules failed: 100% power available
- 1 modules failed: 83% power available
- 2 modules failed: 67% power available

### Rank 5: SSDR_CORELESS

- **Combined Score**: 0.636
- **Fitness**: 0.609
- **Novelty Score**: 0.70 (HIGH)
- **Power**: 3.6 kW
- **Efficiency**: 99.2%
- **Geometry**: D=350mm, p=4, Q=18
- **Modularity**: 6 segments
- **Magnet Segments**: 3
- **Max Temperature**: 70.6C

#### Fault Tolerance Analysis

- 0 modules failed: 100% power available
- 1 modules failed: 83% power available
- 2 modules failed: 67% power available

### Rank 6: DSSR_SLOTTED

- **Combined Score**: 0.577
- **Fitness**: 0.610
- **Novelty Score**: 0.50 (MEDIUM)
- **Power**: 1.5 kW
- **Efficiency**: 97.6%
- **Geometry**: D=200mm, p=4, Q=18
- **Modularity**: 6 segments
- **Magnet Segments**: 4
- **Max Temperature**: 70.8C

#### Fault Tolerance Analysis

- 0 modules failed: 100% power available
- 1 modules failed: 83% power available
- 2 modules failed: 67% power available

### Rank 7: SSDR_CORELESS

- **Combined Score**: 0.561
- **Fitness**: 0.587
- **Novelty Score**: 0.50 (MEDIUM)
- **Power**: 3.6 kW
- **Efficiency**: 99.2%
- **Geometry**: D=200mm, p=6, Q=6
- **Modularity**: 6 segments
- **Magnet Segments**: 4
- **Max Temperature**: 70.6C

#### Fault Tolerance Analysis

- 0 modules failed: 100% power available
- 1 modules failed: 83% power available
- 2 modules failed: 67% power available

### Rank 8: DSSR_SLOTTED

- **Combined Score**: 0.550
- **Fitness**: 0.571
- **Novelty Score**: 0.50 (MEDIUM)
- **Power**: 3.1 kW
- **Efficiency**: 98.7%
- **Geometry**: D=300mm, p=4, Q=9
- **Modularity**: 4 segments
- **Magnet Segments**: 3
- **Max Temperature**: 70.8C

#### Fault Tolerance Analysis

- 0 modules failed: 100% power available
- 1 modules failed: 75% power available
- 2 modules failed: 50% power available

### Rank 9: DSSR_SLOTTED

- **Combined Score**: 0.549
- **Fitness**: 0.571
- **Novelty Score**: 0.50 (MEDIUM)
- **Power**: 2.8 kW
- **Efficiency**: 98.5%
- **Geometry**: D=250mm, p=4, Q=18
- **Modularity**: 4 segments
- **Magnet Segments**: 3
- **Max Temperature**: 70.8C

#### Fault Tolerance Analysis

- 0 modules failed: 100% power available
- 1 modules failed: 75% power available
- 2 modules failed: 50% power available

### Rank 10: DSSR_SLOTTED

- **Combined Score**: 0.538
- **Fitness**: 0.555
- **Novelty Score**: 0.50 (MEDIUM)
- **Power**: 1.1 kW
- **Efficiency**: 96.6%
- **Geometry**: D=150mm, p=4, Q=18
- **Modularity**: 4 segments
- **Magnet Segments**: 2
- **Max Temperature**: 70.7C

#### Fault Tolerance Analysis

- 0 modules failed: 100% power available
- 1 modules failed: 75% power available
- 2 modules failed: 50% power available

## Key Findings

1. **Modular Architecture Benefit**: 6-segment designs score highest on fault tolerance
2. **Magnet Segmentation**: 3-4 segments provide 15% eddy loss reduction
3. **Thermal Co-optimization**: Low-loss designs (<50W) run coolest
4. **Patent Opportunity**: Modular + segmented magnet combinations are novel

## Recommendation

Top candidate (Rank 1) uses:
- DSSR slotted topology (certification-friendly)
- 6 modular segments (83% power after 1 failure)
- 4 magnet segments (15% loss reduction)
- Low pole count (p=4) for manufacturability

This architecture balances aerospace requirements with patentability.