"""Simple lifecycle cash-flow helpers for PV options."""
from __future__ import annotations
import numpy as np


def net_present_value(initial_cost, annual_savings, years, discount_rate,
                      annual_om_cost=0.0, replacement_costs=None):
    if initial_cost < 0 or annual_savings < 0 or years < 1 or discount_rate < 0:
        raise ValueError("invalid project economics inputs")
    replacement_costs = replacement_costs or {}
    npv = -float(initial_cost)
    for year in range(1, int(years) + 1):
        cash = float(annual_savings) - float(annual_om_cost) - float(replacement_costs.get(year, 0.0))
        npv += cash / ((1 + discount_rate) ** year)
    return float(npv)
