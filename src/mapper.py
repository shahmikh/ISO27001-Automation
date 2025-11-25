# src/mapper.py

import json
from pathlib import Path
import pandas as pd
from nlp_matcher import best_policy_match


# -------------------------
# Loaders
# -------------------------

def load_controls(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_mapping_rules(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_policies(folder):
    policies = {}
    p = Path(folder)
    for fp in p.glob("*.txt"):
        policies[fp.name] = fp.read_text(encoding='utf-8')
    return policies


# -------------------------
# Mapping Logic
# -------------------------

def build_mapping_table(controls, rules, policies):
    """
    Returns a DataFrame where each control is mapped to:
      - required evidence types (rule-based)
      - required policies (rule-based)
      - best matching policy (NLP)
      - NLP similarity score
    """
    rows = []

    for control in controls:
        cid = control["id"]
        title = control.get("title", "")
        desc = control.get("description", "")

        # Rule-based requirements
        if cid in rules:
            req_evidence = rules[cid].get("required_evidence", [])
            req_policies = rules[cid].get("required_policies", [])
        else:
            req_evidence = []
            req_policies = []

        # NLP-based matching (policy text → control description)
        best_policy, match_score = best_policy_match(desc, policies)

        rows.append({
            "control_id": cid,
            "title": title,
            "description": desc,
            "required_evidence": ", ".join(req_evidence),
            "required_policies": ", ".join(req_policies),
            "best_policy_match": best_policy,
            "match_score": match_score
        })

    return pd.DataFrame(rows)


# -------------------------
# Main Entrypoint
# -------------------------

def main():
    project_root = Path(__file__).resolve().parents[1]

    controls_path = project_root / "data" / "iso27001_annexA.json"
    mapping_rules_path = project_root / "data" / "control_requirements.json"
    policies_folder = project_root / "policies"
    output_path = project_root / "data" / "mappings.csv"

    print("\n📥 Loading data...")

    controls = load_controls(controls_path)
    rules = load_mapping_rules(mapping_rules_path)
    policies = load_policies(policies_folder)

    print(f"  Controls: {len(controls)} loaded")
    print(f"  Policies: {len(policies)} loaded")
    print(f"  Mapping rules: {len(rules)} entries\n")

    print("⚙️ Building mapping table...")
    df = build_mapping_table(controls, rules, policies)

    df.to_csv(output_path, index=False)

    print(f"✅ Mapping complete! Saved to: {output_path}")
    print("\nPreview:")
    print(df.head())


if __name__ == "__main__":
    main()


