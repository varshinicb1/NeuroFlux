# NeuroFlux Autonomous Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the non-optional autonomous design lab spine for low-speed AFPM generator discovery.

**Architecture:** Keep the Python physics and orchestration backend as the source of truth. Add a lab layer that runs repeated design experiments, stores artifacts, scores novelty against a local patent knowledge graph, critiques designs through a deterministic digital-scientist loop, and exposes JSON outputs suitable for a Rust GUI. The Rust GUI is a consumer of these artifacts, while research-grade FEA and patent ingestion remain engine modules behind stable contracts.

**Tech Stack:** Python 3.10+, Pydantic v2, existing NeuroFlux engines, JSON/Markdown artifacts, pytest, future Rust GUI through artifact manifests.

---

### Task 1: Durable Autonomous Lab Contracts

**Files:**
- Create: `neuroflux/lab/autonomous_lab.py`
- Create: `neuroflux/lab/__init__.py`
- Test: `tests/test_autonomous_lab.py`

- [x] **Step 1: Write tests that require a lab run to create JSON and Markdown artifacts**

```python
def test_autonomous_lab_writes_artifacts(tmp_path):
    lab = AutonomousLab(output_root=tmp_path)
    result = lab.run(config)
    assert (tmp_path / result.run_id / "manifest.json").exists()
    assert (tmp_path / result.run_id / "summary.md").exists()
```

- [x] **Step 2: Implement the lab runner**

The runner must generate candidates through `DiscoveryWorkflow`, produce iteration artifacts, update a manifest, and return a typed `LabRunResult`.

- [x] **Step 3: Run test**

Run: `pytest tests/test_autonomous_lab.py -v`
Expected: PASS.

### Task 2: Patent Knowledge Graph

**Files:**
- Create: `neuroflux/lab/patents.py`
- Test: `tests/test_autonomous_lab.py`

- [x] **Step 1: Add local patent/prior-art graph tests**

```python
graph = PatentKnowledgeGraph.seed_afpm_baseline()
score = graph.score_novelty(candidate_features)
assert 0 <= score.novelty_score <= 1
```

- [x] **Step 2: Implement deterministic novelty scoring**

Use token overlap against seeded AFPM concepts and return closest prior-art references.

### Task 3: Digital Scientist Loop

**Files:**
- Create: `neuroflux/lab/scientist.py`
- Test: `tests/test_autonomous_lab.py`

- [x] **Step 1: Add critique and next-experiment tests**

The scientist must identify target gaps and mutate the next requirement set within safe physical bounds.

- [x] **Step 2: Implement deterministic critique and iteration**

No network or LLM dependency. This preserves reproducibility; future LLM agents can be added behind the same contract.

### Task 4: CLI Runner for Automation and GUI

**Files:**
- Create: `neuroflux/lab/cli.py`
- Modify: `pyproject.toml`
- Test: `tests/test_autonomous_lab.py`

- [x] **Step 1: Add CLI entry point**

Expose `neuroflux-lab run --iterations N --output lab_runs`.

- [x] **Step 2: Test CLI through the Python callable**

Avoid shelling out in unit tests; call `main([...])` and assert artifact creation.

### Task 5: Continuous Operation

**Files:**
- Automation: Codex cron job

- [x] **Step 1: Create a recurring automation**

Run the autonomous lab repeatedly and report test/lab status. The automation must not claim external FEA or patent ingestion unless configured.

### Task 6: Rust GUI Track

**Files:**
- Future create: `gui/neuroflux-gui/`

- [ ] **Step 1: Build an artifact-driven Rust GUI**

The GUI should read `lab_runs/*/manifest.json`, render candidate rankings, open output files, and launch lab iterations through the CLI. This is deliberately downstream of the backend artifact contract so the GUI does not own physics state.

---

Self-review: This plan covers autonomous iteration, artifact output, local patent graph, digital scientist critique, lab CLI, and continuous operation. Research-grade 3D FEA, live patent ingestion, and full Rust GUI are explicitly separate implementation tracks because they require external solver/toolchain validation and cannot be truthfully completed as a single patch.
