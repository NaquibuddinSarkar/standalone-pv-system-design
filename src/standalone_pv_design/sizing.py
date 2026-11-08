"""Preliminary standalone PV system sizing equations.

These calculations are a planning aid, not a construction-ready electrical design.
Confirm site resource, equipment datasheets, standards, wiring/protection and safety.
"""
from __future__ import annotations
import numpy as np


def calculate_daily_energy(load_profile):
    """Return daily energy in kWh from 24 hourly loads in watts."""
    loads = np.asarray(load_profile, dtype=float)
    if loads.ndim != 1 or len(loads) != 24 or np.any(~np.isfinite(loads)) or np.any(loads < 0):
        raise ValueError("load_profile must contain 24 finite non-negative hourly watt values")
    return float(loads.sum() / 1000.0)


def size_pv_array(daily_energy_kwh, peak_sun_hours, system_derate=0.75):
    if daily_energy_kwh <= 0 or peak_sun_hours <= 0 or not 0 < system_derate <= 1:
        raise ValueError("energy and sun hours must be positive; derate must be in (0, 1]")
    return float(daily_energy_kwh / (peak_sun_hours * system_derate))


def size_battery(daily_energy_kwh, autonomy_days, depth_of_discharge=0.8,
                 battery_efficiency=0.9):
    if daily_energy_kwh <= 0 or autonomy_days <= 0:
        raise ValueError("energy and autonomy must be positive")
    if not 0 < depth_of_discharge <= 1 or not 0 < battery_efficiency <= 1:
        raise ValueError("DoD and battery efficiency must be in (0, 1]")
    return float(daily_energy_kwh * autonomy_days / (depth_of_discharge * battery_efficiency))


def size_inverter(peak_load_w, power_factor=0.9, margin=1.25):
    if peak_load_w <= 0 or not 0 < power_factor <= 1 or margin < 1:
        raise ValueError("peak load must be positive; power factor in (0,1]; margin >= 1")
    return float(peak_load_w / (1000 * power_factor) * margin)


def design_system(load_profile_w, peak_sun_hours, autonomy_days, battery_voltage_v=48,
                  system_derate=0.75, depth_of_discharge=0.8, battery_efficiency=0.9,
                  power_factor=0.9, inverter_margin=1.25):
    """Return preliminary sizing metrics from hourly loads in watts."""
    daily_kwh = calculate_daily_energy(load_profile_w)
    pv_kwp = size_pv_array(daily_kwh, peak_sun_hours, system_derate)
    battery_kwh = size_battery(daily_kwh, autonomy_days, depth_of_discharge, battery_efficiency)
    if battery_voltage_v <= 0:
        raise ValueError("battery voltage must be positive")
    peak_w = float(np.max(load_profile_w))
    inverter_kva = size_inverter(peak_w, power_factor, inverter_margin)
    return {
        "daily_energy_kwh": daily_kwh,
        "peak_load_w": peak_w,
        "pv_array_kwp": pv_kwp,
        "battery_nominal_kwh": battery_kwh,
        "battery_capacity_ah": battery_kwh * 1000 / battery_voltage_v,
        "inverter_rating_kva": inverter_kva,
        "charge_controller_current_a_preliminary": pv_kwp * 1000 / battery_voltage_v * 1.25
    }
