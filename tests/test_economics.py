import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from standalone_pv_design.economics import (
    net_present_value,
    levelized_cost_of_energy,
)


def test_npv_includes_replacement_cost():
    no_replacement = net_present_value(100, 20, 5, 0.1)
    replacement = net_present_value(100, 20, 5, 0.1, replacement_costs={3: 30})
    assert replacement < no_replacement


def test_lcoe_is_positive_and_degradation_changes_result():
    base = levelized_cost_of_energy(
        initial_cost=100000,
        annual_om_cost=2000,
        annual_energy_kwh=10000,
        years=20,
        discount_rate=0.08,
    )
    degraded = levelized_cost_of_energy(
        initial_cost=100000,
        annual_om_cost=2000,
        annual_energy_kwh=10000,
        years=20,
        discount_rate=0.08,
        annual_energy_degradation=0.01,
    )
    assert base > 0
    assert degraded > base


def test_lcoe_rejects_invalid_energy():
    with pytest.raises(ValueError):
        levelized_cost_of_energy(1000, 20, 0, 20, 0.08)
