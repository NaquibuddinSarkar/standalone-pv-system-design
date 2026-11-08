"""Preliminary standalone PV sizing and hourly battery-dispatch calculations.

All equations are screening approximations. Final component selection requires
site-specific resource data, manufacturer datasheets, electrical protection
design and review by a qualified electrical engineer.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


STANDARD_CABLE_MM2 = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]


def validate_load_profile(load_profile_w, interval_hours=1.0):
    """Validate an aggregate load profile in watts and return a numeric array.

    The profile can contain 24 hourly values or another regular interval.
    The interval length must be specified correctly; do not pass daily energy
    totals as if they were instantaneous power values.
    """
    loads = np.asarray(load_profile_w, dtype=float)
    if loads.ndim != 1 or loads.size == 0:
        raise ValueError("load profile must be a non-empty one-dimensional array")
    if not np.isfinite(loads).all() or np.any(loads < 0):
        raise ValueError("load profile must contain finite non-negative watt values")
    if not np.isfinite(interval_hours) or interval_hours <= 0:
        raise ValueError("interval_hours must be a positive finite number")
    return loads


def calculate_daily_energy(load_profile_w, interval_hours=1.0):
    """Return energy in kWh for the supplied representative-day profile."""
    loads = validate_load_profile(load_profile_w, interval_hours)
    if not np.isclose(loads.size * interval_hours, 24.0):
        raise ValueError("a representative daily profile must cover exactly 24 hours")
    return float(loads.sum() * interval_hours / 1000.0)


def size_pv_array(daily_energy_kwh, peak_sun_hours, system_derate=0.75,
                  inverter_efficiency=1.0):
    """Estimate PV kWp from daily AC energy, PSH, derate and inverter efficiency.

    system_derate is the combined PV-side performance ratio before the
    inverter. It should capture temperature, soiling, mismatch, wiring and
    controller/battery losses to the extent represented by the chosen design.
    """
    values = [daily_energy_kwh, peak_sun_hours, system_derate, inverter_efficiency]
    if not np.isfinite(values).all():
        raise ValueError("PV sizing inputs must be finite")
    if daily_energy_kwh <= 0 or peak_sun_hours <= 0:
        raise ValueError("daily energy and peak sun hours must be positive")
    if not 0 < system_derate <= 1 or not 0 < inverter_efficiency <= 1:
        raise ValueError("derate and inverter efficiency must be in (0, 1]")
    return float(daily_energy_kwh / (peak_sun_hours * system_derate * inverter_efficiency))


def size_battery(daily_energy_kwh, autonomy_days, depth_of_discharge=0.8,
                 battery_efficiency=0.9, inverter_efficiency=1.0):
    """Estimate nominal battery energy for an AC load and autonomy target.

    battery_efficiency is treated as a one-way discharge/conversion factor
    from nominal battery energy to the DC energy available to the inverter.
    DoD is the permitted usable fraction of nominal capacity.
    """
    values = [daily_energy_kwh, autonomy_days, depth_of_discharge,
              battery_efficiency, inverter_efficiency]
    if not np.isfinite(values).all():
        raise ValueError("battery sizing inputs must be finite")
    if daily_energy_kwh <= 0 or autonomy_days <= 0:
        raise ValueError("daily energy and autonomy must be positive")
    if not 0 < depth_of_discharge <= 1:
        raise ValueError("depth_of_discharge must be in (0, 1]")
    if not 0 < battery_efficiency <= 1 or not 0 < inverter_efficiency <= 1:
        raise ValueError("battery and inverter efficiencies must be in (0, 1]")
    return float(
        daily_energy_kwh * autonomy_days
        / (depth_of_discharge * battery_efficiency * inverter_efficiency)
    )


def size_inverter(peak_load_w, power_factor=0.9, margin=1.25):
    """Estimate continuous inverter apparent-power rating in kVA."""
    if not np.isfinite([peak_load_w, power_factor, margin]).all():
        raise ValueError("inverter sizing inputs must be finite")
    if peak_load_w <= 0 or not 0 < power_factor <= 1 or margin < 1:
        raise ValueError("peak load must be positive; PF in (0,1]; margin >= 1")
    return float(peak_load_w / (1000.0 * power_factor) * margin)


def design_system(
    load_profile_w,
    peak_sun_hours,
    autonomy_days,
    battery_voltage_v=48,
    system_derate=0.75,
    depth_of_discharge=0.8,
    battery_efficiency=0.9,
    power_factor=0.9,
    inverter_margin=1.25,
    inverter_efficiency=0.92,
    interval_hours=1.0,
    charge_controller_safety_factor=1.25,
):
    """Return a first-pass daily-energy, PV, battery and inverter sizing summary."""
    loads = validate_load_profile(load_profile_w, interval_hours)
    daily_kwh = calculate_daily_energy(loads, interval_hours)
    peak_w = float(loads.max())
    if not np.isfinite(battery_voltage_v) or battery_voltage_v <= 0:
        raise ValueError("battery_voltage_v must be positive and finite")
    if not np.isfinite(charge_controller_safety_factor) or charge_controller_safety_factor < 1:
        raise ValueError("charge controller safety factor must be at least 1")

    pv_kwp = size_pv_array(
        daily_kwh, peak_sun_hours, system_derate, inverter_efficiency
    )
    battery_kwh = size_battery(
        daily_kwh, autonomy_days, depth_of_discharge,
        battery_efficiency, inverter_efficiency
    )
    inverter_kva = size_inverter(peak_w, power_factor, inverter_margin)
    battery_ah = battery_kwh * 1000.0 / battery_voltage_v
    controller_output_current = (
        pv_kwp * 1000.0 / battery_voltage_v * charge_controller_safety_factor
    )

    return {
        "daily_energy_kwh": daily_kwh,
        "peak_load_w": peak_w,
        "pv_array_kwp_preliminary": pv_kwp,
        "pv_array_kwp": pv_kwp,
        "battery_nominal_kwh_preliminary": battery_kwh,
        "battery_nominal_kwh": battery_kwh,
        "battery_capacity_ah_at_nominal_voltage": battery_ah,
        "battery_capacity_ah": battery_ah,
        "inverter_continuous_kva_preliminary": inverter_kva,
        "inverter_rating_kva": inverter_kva,
        "charge_controller_output_current_a_preliminary": controller_output_current,
        "charge_controller_current_a_preliminary": controller_output_current,
        "assumptions": {
            "peak_sun_hours": float(peak_sun_hours),
            "system_derate": float(system_derate),
            "inverter_efficiency": float(inverter_efficiency),
            "battery_efficiency": float(battery_efficiency),
            "depth_of_discharge": float(depth_of_discharge),
            "autonomy_days": float(autonomy_days),
            "interval_hours": float(interval_hours),
        },
        "design_note": (
            "Preliminary sizing only. Verify seasonal resource, module temperature, "
            "cold-corrected Voc, Isc, controller limits, battery C-rate, inverter surge, "
            "cable ampacity/voltage drop, protection, grounding and applicable code."
        ),
    }


def check_pv_string_configuration(
    module_voc_v,
    modules_in_series,
    modules_in_parallel,
    minimum_ambient_temperature_c,
    voc_temperature_coefficient_per_c,
    controller_max_pv_voltage_v,
    module_isc_a,
    controller_max_input_current_a,
    voltage_design_margin=0.95,
    current_design_margin=1.25,
):
    """Perform basic PV-string voltage and current screening checks.

    The Voc temperature coefficient is entered as a fractional change per °C
    (often negative, e.g. -0.0028 per °C). Use the actual module datasheet.
    This check does not replace full IEC/system design or protection review.
    """
    inputs = [
        module_voc_v, minimum_ambient_temperature_c,
        voc_temperature_coefficient_per_c, controller_max_pv_voltage_v,
        module_isc_a, controller_max_input_current_a,
        voltage_design_margin, current_design_margin,
    ]
    if not np.isfinite(inputs).all():
        raise ValueError("string-check inputs must be finite")
    if module_voc_v <= 0 or module_isc_a <= 0 or controller_max_pv_voltage_v <= 0:
        raise ValueError("module and controller ratings must be positive")
    if (not isinstance(modules_in_series, (int, np.integer))
            or not isinstance(modules_in_parallel, (int, np.integer))
            or modules_in_series < 1 or modules_in_parallel < 1):
        raise ValueError("series and parallel counts must be positive integers")
    if not 0 < voltage_design_margin <= 1 or current_design_margin < 1:
        raise ValueError("invalid design margins")
    corrected_voc_per_module = module_voc_v * (
        1.0 + voc_temperature_coefficient_per_c * (minimum_ambient_temperature_c - 25.0)
    )
    if corrected_voc_per_module <= 0:
        raise ValueError("corrected module Voc is non-positive; check datasheet coefficient")
    string_voc = corrected_voc_per_module * modules_in_series
    array_isc_design = module_isc_a * modules_in_parallel * current_design_margin
    max_allowed_voltage = controller_max_pv_voltage_v * voltage_design_margin
    return {
        "corrected_module_voc_v": float(corrected_voc_per_module),
        "cold_corrected_string_voc_v": float(string_voc),
        "design_array_isc_a": float(array_isc_design),
        "controller_voltage_limit_v": float(max_allowed_voltage),
        "voltage_check_pass": bool(string_voc <= max_allowed_voltage),
        "current_check_pass": bool(array_isc_design <= controller_max_input_current_a),
        "note": "Screening calculation only; apply local code and manufacturer rules.",
    }


def simulate_hourly_dispatch(
    load_kw,
    pv_generation_kw,
    battery_capacity_kwh,
    initial_soc_fraction=0.8,
    minimum_soc_fraction=0.2,
    charge_efficiency=0.95,
    discharge_efficiency=0.95,
    interval_hours=1.0,
    max_charge_kw=None,
    max_discharge_kw=None,
):
    """Simulate simple PV-load-battery energy dispatch over aligned time steps.

    PV serves the load first. Surplus charges the battery; remaining surplus is
    curtailed. When PV is insufficient, the battery discharges down to its
    minimum SOC; any remaining deficit is unserved energy.

    This is an educational energy-balance model, not an electrochemical battery
    model. It omits voltage-dependent power limits, temperature, C-rate curves,
    inverter efficiency maps, degradation and protection behaviour.
    """
    load = np.asarray(load_kw, dtype=float)
    pv = np.asarray(pv_generation_kw, dtype=float)
    if load.ndim != 1 or pv.ndim != 1 or len(load) == 0 or len(load) != len(pv):
        raise ValueError("load_kw and pv_generation_kw must be non-empty aligned vectors")
    if not np.isfinite(load).all() or not np.isfinite(pv).all():
        raise ValueError("load and PV profiles must be finite")
    if np.any(load < 0) or np.any(pv < 0):
        raise ValueError("load and PV generation cannot be negative")
    if not np.isfinite(battery_capacity_kwh) or battery_capacity_kwh < 0:
        raise ValueError("battery capacity must be finite and non-negative")
    if not 0 <= minimum_soc_fraction <= initial_soc_fraction <= 1:
        raise ValueError("SOC must satisfy 0 <= minimum <= initial <= 1")
    if not 0 < charge_efficiency <= 1 or not 0 < discharge_efficiency <= 1:
        raise ValueError("battery efficiencies must be in (0,1]")
    if not np.isfinite(interval_hours) or interval_hours <= 0:
        raise ValueError("interval_hours must be positive")
    max_charge_kw = np.inf if max_charge_kw is None else float(max_charge_kw)
    max_discharge_kw = np.inf if max_discharge_kw is None else float(max_discharge_kw)
    if max_charge_kw <= 0 or max_discharge_kw <= 0:
        raise ValueError("charge/discharge power limits must be positive")

    stored = battery_capacity_kwh * initial_soc_fraction
    minimum_stored = battery_capacity_kwh * minimum_soc_fraction
    rows = []
    for step, (load_power, pv_power) in enumerate(zip(load, pv)):
        direct_pv = min(load_power, pv_power)
        surplus_kw = max(pv_power - direct_pv, 0.0)
        deficit_kw = max(load_power - direct_pv, 0.0)

        charge_input_kw = min(surplus_kw, max_charge_kw)
        possible_store = charge_input_kw * interval_hours * charge_efficiency
        room = max(battery_capacity_kwh - stored, 0.0)
        stored_energy = min(possible_store, room)
        stored += stored_energy
        actual_charge_input = stored_energy / (interval_hours * charge_efficiency)
        curtailed_kw = max(surplus_kw - actual_charge_input, 0.0)

        available_stored = max(stored - minimum_stored, 0.0)
        delivered_kw = min(
            deficit_kw,
            max_discharge_kw,
            available_stored * discharge_efficiency / interval_hours,
        )
        withdrawn_energy = delivered_kw * interval_hours / discharge_efficiency
        stored -= withdrawn_energy
        unserved_kw = max(deficit_kw - delivered_kw, 0.0)

        rows.append({
            "step": step,
            "load_kw": float(load_power),
            "pv_kw": float(pv_power),
            "direct_pv_to_load_kw": float(direct_pv),
            "battery_charge_input_kw": float(actual_charge_input),
            "battery_discharge_to_load_kw": float(delivered_kw),
            "unserved_load_kw": float(unserved_kw),
            "curtailed_pv_kw": float(curtailed_kw),
            "battery_soc_kwh": float(stored),
            "battery_soc_fraction": float(stored / battery_capacity_kwh) if battery_capacity_kwh else 0.0,
        })

    result = pd.DataFrame(rows)
    result.attrs["unserved_energy_kwh"] = float(result["unserved_load_kw"].sum() * interval_hours)
    result.attrs["curtailed_energy_kwh"] = float(result["curtailed_pv_kw"].sum() * interval_hours)
    result.attrs["served_energy_kwh"] = float(
        (result["load_kw"] - result["unserved_load_kw"]).sum() * interval_hours
    )
    return result


def cable_area_mm2(current_a, one_way_length_m, system_voltage_v,
                   voltage_drop_pct=2.0, resistivity_ohm_mm2_per_m=0.0175):
    """Estimate DC two-conductor copper area from voltage-drop limit only.

    This calculation does not verify ampacity, short-circuit withstand,
    protective-device coordination, installation method or derating factors.
    """
    inputs = [current_a, one_way_length_m, system_voltage_v,
              voltage_drop_pct, resistivity_ohm_mm2_per_m]
    if not np.isfinite(inputs).all() or min(inputs) <= 0:
        raise ValueError("cable calculation inputs must be positive finite values")
    delta_v = system_voltage_v * voltage_drop_pct / 100.0
    required_area = (
        2.0 * one_way_length_m * current_a * resistivity_ohm_mm2_per_m / delta_v
    )
    selected = next((size for size in STANDARD_CABLE_MM2 if size >= required_area), None)
    return {
        "required_area_mm2_voltage_drop_only": float(required_area),
        "next_standard_area_mm2": selected,
        "note": (
            "Preliminary voltage-drop estimate only. Ampacity, temperature, grouping, "
            "installation method and fault protection may require a larger conductor."
        ),
    }
