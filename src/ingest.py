# src/ingest.py
import json
import os
import pandas as pd
from pathlib import Path

def load_controls(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_assets(path):
    return pd.read_csv(path)

def load_policies(folder):
    policies = {}
    p = Path(folder)
    for fp in p.glob("*.txt"):
        policies[fp.name] = fp.read_text(encoding='utf-8')
    return policies

def load_risk_register(path):
    return pd.read_csv(path)

def load_evidence_index(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    base = Path(__file__).resolve().parents[1] / "data"
    controls_path = base / "iso27001_annexA.json"
    assets_path = base / "assets.csv"
    policies_folder = Path(__file__).resolve().parents[1] / "policies"
    risk_path = base / "risk_register.csv"
    evidence_path = base / "evidence_index.json"

    print("Loading controls...")
    controls = load_controls(controls_path)
    print(f"Controls loaded: {len(controls)} (showing first 3)")
    for c in controls[:3]:
        print(f"  - {c.get('id')}: {c.get('title')}")

    print("\nLoading assets...")
    assets = load_assets(assets_path)
    print(f"Assets loaded: {len(assets)}")
    print(assets.head().to_string(index=False))

    print("\nLoading policies...")
    policies = load_policies(policies_folder)
    print(f"Policies loaded: {len(policies)}")
    for name in policies:
        print(f"  - {name}")

    print("\nLoading risk register...")
    risks = load_risk_register(risk_path)
    print(f"Risks loaded: {len(risks)}")
    print(risks.head().to_string(index=False))

    print("\nLoading evidence index...")
    evidence = load_evidence_index(evidence_path)
    print(f"Evidence entries: {len(evidence.get('evidence', []))}")
    for e in evidence.get('evidence', [])[:3]:
        print(f"  - {e.get('id')}: {e.get('type')} -> {e.get('path')}")

if __name__ == '__main__':
    main()
