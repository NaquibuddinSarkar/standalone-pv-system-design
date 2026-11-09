import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from standalone_pv_design.sizing import (
    calculate_daily_energy,
    size_pv_array,
    size_battery,
    size_inverter,
    design_system,
    check_pv_string_configuration,
    simulate_hourly_dispatch,
    cable_area_mm2,
)
from standalone_pv_design.economics import net_present_value, levelized_cost_of_energy


def test_daily_energy():
    assert calculate_daily_energy(np.full(24, 100.0)) == pytest.approx(2.4)


def test_daily_energy_accepts_half_hour_intervals():
    assert calculate_daily_energy(np.full(48, 100.0), interval_hours=0.5) == pytest.approx(2.4)


def test_daily_energy_requires_full_day():
    with pytest.raises(ValueError):
        calculate_daily_energy([10, 20])


def test_pv_sizing():
    assert size_pv_array(5, 5, .8) == pytest.approx(1.25)


def test_battery_sizing():
    assert size_battery(5, 2, .8, .9) == pytest.approx(13.8888889)


def test_design_outputs_positive_and_compatible():
    result = design_system(np.full(24, 200.0), 4.5, 1)
    assert result["pv_array_kwp"] > 0
    assert result["battery_capacity_ah"] > 0
    assert result["inverter_rating_kva"] > 0
    assert result["assumptions"]["inverter_efficiency"] > 0


def test_invalid_load_rejected():
    with pytest.raises(ValueError):
        calculate_daily_energy([10, 20])


def test_pv_string_checks_cold_voc_and_current():
    result = check_pv_string_configuration(
        module_voc_v=49.5,
        modules_in_series=5,
        modules_in_parallel=2,
        minimum_ambient_temperature_c=5,
        voc_temperature_coefficient_per_c=-0.0028,
        controller_max_pv_voltage_v=300,
        module_isc_a=13.0,
        controller_max_input_current_a=35,
    )
    assert result["cold_corrected_string_voc_v"] > 49.5 * 5
    assert result["voltage_check_pass"]
    assert result["current_check_pass"]


def test_dispatch_tracks_unserved_and_curtailed_energy():
    result = simulate_hourly_dispatch(
        load_kw=[1.0, 1.0, 1.0],
        pv_generation_kw=[2.0, 0.0, 0.0],
        battery_capacity_kwh=1.5,
        initial_soc_fraction=0.2,
        minimum_soc_fraction=0.0,
        charge_efficiency=1.0,
        discharge_efficiency=1.0,
    )
    assert result.attrs["served_energy_kwh"] <= 3.0
    assert result.attrs["unserved_energy_kwh"] == pytest.approx(0.7)
    assert result.attrs["curtailed_energy_kwh"] == pytest.approx(0.0)


def test_cable_area_rejects_invalid_voltage():
    with pytest.raises(ValueError):
        cable_area_mm2(10, 20, 0)


def test_lcoe_is_positive_and_degradation_changes_result():
    base = levelized_cost_of_energy(
        initial_cost=100000, annual_om_cost=2000,
        annual_energy_kwh=10000, years=20, discount_rate=.08
    )
    degraded = levelized_cost_of_energy(
        initial_cost=100000, annual_om_cost=2000,
        annual_energy_kwh=10000, years=20, discount_rate=.08,
        annual_energy_degradation=.01
    )
    assert base > 0
    assert degraded > base


def test_npv_includes_replacement_cost():
    no_replacement = net_present_value(100, 20, 5, .1)
    replacement = net_present_value(100, 20, 5, .1, replacement_costs={3: 30})
    assert replacement < no_replacement
