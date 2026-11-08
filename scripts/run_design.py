"""Run preliminary standalone PV sizing using the synthetic example load profile."""
from pathlib import Path
import json
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from standalone_pv_design.sizing import design_system


def main():
    cfg = json.loads((ROOT / "config" / "design.json").read_text())
    load_path = ROOT / "data" / "demo" / "load_profile_synthetic.csv"
    loads = pd.read_csv(load_path)["load_w"].to_numpy()

    result = design_system(
        load_profile_w=loads,
        peak_sun_hours=cfg["peak_sun_hours"],
        autonomy_days=cfg["autonomy_days"],
        battery_voltage_v=cfg["battery_voltage_v"],
        system_derate=cfg["system_derate"],
        depth_of_discharge=cfg["depth_of_discharge"],
        battery_efficiency=cfg["battery_efficiency"],
        power_factor=cfg["power_factor"],
        inverter_margin=cfg["inverter_margin"],
        inverter_efficiency=cfg.get("inverter_efficiency", 0.92),
        interval_hours=cfg.get("interval_hours", 1.0),
        charge_controller_safety_factor=cfg.get("charge_controller_safety_factor", 1.25),
    )
    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "preliminary_design_demo.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print("\nWARNING: Synthetic load and illustrative resource assumptions. "
          "This is not a construction-ready electrical design.")


if __name__ == "__main__":
    main()
