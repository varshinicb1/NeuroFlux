"""
Unit tests for NeuroFlux materials config validation.
"""

from __future__ import annotations

from neuroflux.core.materials import MaterialDatabase


def test_pm_grades():
    """Verifies that magnet properties load correctly."""
    db = MaterialDatabase()
    n42 = db.get_pm("N42")
    assert n42.Br > 1.2
    assert n42.Hcj > 800e3
    
    ferrite = db.get_pm("Y30BH")
    assert ferrite.Br < 0.5


def test_default_config():
    """Verifies that default configuration loads all required components."""
    db = MaterialDatabase()
    config = db.build_material_properties("N42", "M600-50A")
    assert config.Br > 1.2
    assert config.k_hys > 100.0
