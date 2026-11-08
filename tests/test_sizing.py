import sys
from pathlib import Path
import numpy as np
import pytest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from standalone_pv_design.sizing import (
    calculate_daily_energy, size_pv_array, size_battery, size_inverter, design_system
)


def test_daily_energy():
    assert calculate_daily_energy(np.full(24, 100.0)) == pytest.approx(2.4)


def test_pv_sizing():
    assert size_pv_array(5, 5, .8) == pytest.approx(1.25)


def test_battery_sizing():
    assert size_battery(5, 2, .8, .9) == pytest.approx(13.8888889)


def test_design_outputs_positive():
    result = design_system(np.full(24, 200.0), 4.5, 1)
    assert result["pv_array_kwp"] > 0
    assert result["battery_capacity_ah"] > 0
    assert result["inverter_rating_kva"] > 0


def test_invalid_load_rejected():
    with pytest.raises(ValueError):
        calculate_daily_energy([10, 20])
