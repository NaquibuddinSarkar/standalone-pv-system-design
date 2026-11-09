# Standalone PV preliminary design method

This document explains the equations in the code and identifies the checks that remain outside the simplified model. All numerical examples in the repository use a synthetic load profile and illustrative solar-resource assumptions.

## 1. Load assessment

For an appliance with power P watts, quantity n and operating time h hours/day:

`E = n × P × h / 1000` kWh/day.

The aggregate daily load is the sum across appliances. The maximum coincident load is not necessarily the sum of all rated appliance powers; use a realistic time profile. For pumps, compressors and other motors, capture starting current and surge duration.

## 2. PV array estimate

The screening calculation uses:

`PV kWp = daily AC energy / (PSH × PV-side derate × inverter efficiency)`

PSH is equivalent peak-sun-hours for the chosen site and period. The derate factor is an aggregate PV-side performance ratio; do not double-count losses already included in it. A full design should separate module temperature, soiling, mismatch, DC wiring, controller, storage and availability effects.

Use monthly resource data and design for the critical season. An annual-average PSH can overstate the array's ability to meet loads during a poor-solar month.

## 3. Battery energy

The nominal battery-energy estimate is:

`Battery kWh = daily AC energy × autonomy days / (DoD × discharge efficiency × inverter efficiency)`

The result is only a first-pass energy requirement. Validate battery chemistry, C-rate, temperature, end-of-life capacity, cycle life, low-voltage cut-off and the manufacturer's operating window.

## 4. Inverter and controller

Inverter apparent power is screened from peak real power divided by power factor, then multiplied by a sizing margin. Final selection must consider continuous kW/kVA, surge kVA and duration, motor start, harmonics and temperature derating.

Charge controller sizing must respect PV input voltage and current limits. The helper `check_pv_string_configuration` corrects module Voc for a minimum temperature using the supplied module temperature coefficient, then compares string Voc and array Isc with controller limits. Use the datasheet coefficient and the design minimum ambient temperature. The simple check does not replace code-specific current multipliers or all protection requirements.

## 5. Hourly dispatch

The hourly dispatch helper:
1. uses PV to serve load first;
2. charges the battery from excess PV up to its energy and power limits;
3. discharges the battery when PV is insufficient, down to minimum state of charge;
4. records unserved load and curtailed PV.

It is not an electrochemical battery model. It omits voltage, temperature, C-rate curves, inverter efficiency maps, degradation, battery management and equipment faults. Extend it before using loss-of-load metrics in a real design.

## 6. Cable voltage drop

The cable helper estimates a DC two-conductor copper area from a selected voltage-drop limit:

`A = 2 × L × I × rho / DeltaV`

It is only a voltage-drop estimate. Ampacity, installation method, ambient temperature, cable grouping, fault current, protection coordination and earthing may require a larger size or another design.

## 7. Lifecycle economics

The LCOE helper calculates discounted lifecycle costs divided by discounted delivered energy. The user must keep price-year and discount-rate conventions consistent. Include replacement costs and degradation where relevant. A positive NPV or low LCOE does not confirm technical compliance or reliability.

## 8. Final engineering review

Before installation, a qualified engineer must verify site survey, array layout, structural loading, module/string calculations, battery protection, DC and AC cable sizing, protective devices, earthing, lightning/surge protection, isolation, signage, commissioning and applicable Bangladesh rules/standards.
