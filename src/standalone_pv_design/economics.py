"""Discounted cash-flow helpers for preliminary PV option comparison.

All monetary inputs must use one consistent currency and price-year basis.
The functions do not calculate tax, financing or working capital unless those
items are explicitly represented by the analyst.
"""
from __future__ import annotations

import numpy as np


def _validate_rate(discount_rate):
    if not np.isfinite(discount_rate) or discount_rate <= -1:
        raise ValueError("discount_rate must be finite and greater than -1")


def _validate_years(years):
    if not isinstance(years, (int, np.integer)) or years < 1:
        raise ValueError("years must be a positive integer")


def _normalise_replacements(replacement_costs, years):
    if replacement_costs is None:
        return {}
    if not isinstance(replacement_costs, dict):
        raise TypeError("replacement_costs must be a {year: cost} dictionary")
    normalised = {}
    for year, cost in replacement_costs.items():
        try:
            year_int = int(year)
        except (TypeError, ValueError) as exc:
            raise ValueError("replacement-cost keys must be integer years") from exc
        if str(year_int) != str(year) and not isinstance(year, (int, np.integer)):
            raise ValueError("replacement-cost keys must be canonical integer years")
        if year_int < 1 or year_int > years:
            raise ValueError("replacement cost year must lie within project life")
        if year_int in normalised:
            raise ValueError("replacement-cost years must be unique")
        if not np.isfinite(cost) or cost < 0:
            raise ValueError("replacement costs must be finite and non-negative")
        normalised[year_int] = float(cost)
    return normalised


def net_present_value(initial_cost, annual_savings, years, discount_rate,
                      annual_om_cost=0.0, replacement_costs=None):
    """NPV of avoided energy cost less O&M and year-specific replacements.

    Year zero is the initial capital cost. Annual savings and O&M are assumed
    constant in nominal terms; add escalation/inflation explicitly if needed.
    """
    _validate_rate(discount_rate)
    _validate_years(years)
    if not np.isfinite([initial_cost, annual_savings, annual_om_cost]).all():
        raise ValueError("cash-flow inputs must be finite")
    if initial_cost < 0 or annual_savings < 0 or annual_om_cost < 0:
        raise ValueError("costs and annual savings must be non-negative")
    replacements = _normalise_replacements(replacement_costs, years)

    result = -float(initial_cost)
    for year in range(1, int(years) + 1):
        cash = (
            float(annual_savings)
            - float(annual_om_cost)
            - replacements.get(year, 0.0)
        )
        result += cash / ((1.0 + discount_rate) ** year)
    return float(result)


def levelized_cost_of_energy(initial_cost, annual_om_cost, annual_energy_kwh,
                             years, discount_rate, replacement_costs=None,
                             annual_energy_degradation=0.0, salvage_value=0.0):
    """Calculate screening LCOE as discounted lifetime cost / discounted energy.

    The first-year energy is assumed to occur in year 1. Annual energy declines
    by a constant fractional degradation rate. Costs are assumed constant in
    nominal terms except the explicit replacement schedule. If using real
    prices, use a real discount rate; if using nominal prices, model escalation
    consistently and use a nominal rate.
    """
    _validate_rate(discount_rate)
    _validate_years(years)
    if not np.isfinite([
        initial_cost, annual_om_cost, annual_energy_kwh,
        annual_energy_degradation, salvage_value,
    ]).all():
        raise ValueError("LCOE inputs must be finite")
    if initial_cost < 0 or annual_om_cost < 0 or annual_energy_kwh <= 0:
        raise ValueError("invalid cost or energy input")
    if not 0 <= annual_energy_degradation < 1 or salvage_value < 0:
        raise ValueError("degradation must be in [0,1) and salvage value non-negative")
    replacements = _normalise_replacements(replacement_costs, years)

    discounted_cost = float(initial_cost)
    discounted_energy = 0.0
    for year in range(1, int(years) + 1):
        discounted_cost += (
            float(annual_om_cost) + replacements.get(year, 0.0)
        ) / ((1.0 + discount_rate) ** year)
        energy = annual_energy_kwh * ((1.0 - annual_energy_degradation) ** (year - 1))
        discounted_energy += energy / ((1.0 + discount_rate) ** year)
    discounted_cost -= salvage_value / ((1.0 + discount_rate) ** int(years))
    if discounted_energy <= 0 or discounted_cost < 0:
        raise ValueError("discounted lifetime cost and energy must be physically meaningful")
    return float(discounted_cost / discounted_energy)
