"""Run preliminary sizing using the synthetic example load profile."""
from pathlib import Path
import json
import sys
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from standalone_pv_design.sizing import design_system


def main():
    cfg = json.loads((ROOT / "config" / "design.json").read_text())
    loads = pd.read_csv(ROOT / "data" / "demo" / "load_profile_synthetic.csv")["load_w"].to_numpy()
    result = design_system(
        loads, cfg["peak_sun_hours"], cfg["autonomy_days"],
        cfg["battery_voltage_v"], cfg["system_derate"],
        cfg["depth_of_discharge"], cfg["battery_efficiency"],
        cfg["power_factor"], cfg["inverter_margin"]
    )
    print(json.dumps(result, indent=2))
    print("\nWARNING: Demo load/resource assumptions are illustrative. Obtain site-specific inputs before design.")


if __name__ == "__main__":
    main()
