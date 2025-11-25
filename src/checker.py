# src/checker.py

import json
import csv
from pathlib import Path
import pandas as pd


# -------------------------
# Data Loaders
# -------------------------

def load_mappings(path):
    return pd.read_csv(path)

def load_evidence_index(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f).get('evidence', [])


# -------------------------
# Evidence Checking Helpers
# -------------------------

def evidence_exists_by_type(evidence_index, evidence_type):
    """
    Return True if any evidence item has the given type.
    Types include: policy, config, asset_inventory
    """
    for e in evidence_index:
        if e.get('type') == evidence_type:
            return True
    return False

def evidence_exists_policy(evidence_index, policy_name):
    """
    Check policy availability by matching filename or path.
    Accepts base name (acceptable_use) or file (acceptable_use.txt)
    """
    if not policy_name:
        return False

    # Normalize
    normalized = policy_name.replace(".txt", "")

    for e in evidence_index:
        name = e.get("name", "")
        path = e.get("path", "")

        # Match by filename without extension
        if normalized in name.replace(".txt", ""):
            return True

        # Match by path suffix
        if path.endswith(normalized + ".txt"):
            return True

    return False


# -------------------------
# Control Weighting (Risk-Based Scoring)
# -------------------------

def calculate_control_weight(control_title):
    """
    Simple heuristic to assign risk weights.
    High-impact controls contribute more to overall score.
    """
    title_lower = control_title.lower()

    if "access" in title_lower:
        return 2.0  # Access Control = high criticality
    if "cryptograph" in title_lower:
        return 2.0  # Encryption is high criticality
    if "asset" in title_lower:
        return 1.5
    if "physical" in title_lower:
        return 1.5

    return 1.0  # default weight


# -------------------------
# Core Evaluation Logic
# -------------------------

def evaluate_control(row, evidence_index):
    """
    Evaluate a single ISO control for compliance.
    Returns missing items and remediation suggestions.
    """
    control_id = row['control_id']

    req_evidence = [s.strip() for s in str(row.get('required_evidence', '')).split(',') if s.strip()]
    req_policies = [s.strip() for s in str(row.get('required_policies', '')).split(',') if s.strip()]

    missing_evidence = []
    missing_policies = []

    # Evidence types check
    for et in req_evidence:
        if not evidence_exists_by_type(evidence_index, et):
            missing_evidence.append(et)

    # Policies check
    for pol in req_policies:
        if not evidence_exists_policy(evidence_index, pol):
            missing_policies.append(pol)

    # Determine compliance status
    if not missing_evidence and not missing_policies:
        status = "Compliant"
    elif missing_evidence and missing_policies:
        status = "Not Compliant"
    else:
        status = "Partially Compliant"

    remediation = []
    if missing_evidence:
        remediation.append(
            f"Provide evidence types: {', '.join(missing_evidence)} "
            "(e.g., configs, screenshots, inventory)"
        )
    if missing_policies:
        remediation.append(
            f"Publish or update policies: {', '.join(missing_policies)} "
            "(add PDF/TXT to policies/ + reference in evidence_index.json)"
        )

    return {
        "control_id": control_id,
        "status": status,
        "missing_evidence": missing_evidence,
        "missing_policies": missing_policies,
        "remediation": remediation
    }


# -------------------------
# Main Execution
# -------------------------

def main():
    project_root = Path(__file__).resolve().parents[1]

    mappings_path = project_root / "data" / "mappings.csv"
    evidence_index_path = project_root / "data" / "evidence_index.json"

    print("🔎 Loading mappings and evidence index...")

    mappings = load_mappings(mappings_path)
    evidence_index = load_evidence_index(evidence_index_path)

    results = []
    gaps_rows = []

    # ---- Evaluate Each Control ----
    for _, row in mappings.iterrows():
        res = evaluate_control(row, evidence_index)

        control_title = row.get('title', '')
        weight = calculate_control_weight(control_title)

        status = res['status']
        if status == "Compliant":
            weighted_score = 1 * weight
        elif status == "Partially Compliant":
            weighted_score = 0.5 * weight
        else:
            weighted_score = 0

        results.append({
            "control_id": res['control_id'],
            "title": control_title,
            "status": status,
            "weight": weight,
            "weighted_score": weighted_score,
            "missing_evidence": res['missing_evidence'],
            "missing_policies": res['missing_policies'],
            "best_policy_match": row.get('best_policy_match', ''),
            "match_score": row.get('match_score', '')
        })

        # Gaps CSV
        if res['missing_evidence'] or res['missing_policies']:
            gaps_rows.append({
                "control_id": res['control_id'],
                "title": control_title,
                "missing_evidence": "; ".join(res['missing_evidence']),
                "missing_policies": "; ".join(res['missing_policies']),
                "remediation": " | ".join(res['remediation'])
            })

    # ---- Save JSON Results ----
    results_path = project_root / "data" / "results.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    # ---- Save Gaps CSV ----
    gaps_path = project_root / "data" / "gaps.csv"
    with open(gaps_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["control_id", "title", "missing_evidence", "missing_policies", "remediation"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in gaps_rows:
            writer.writerow(r)

    # ---- Compliance Summary ----
    total = len(results)
    compliant = sum(1 for r in results if r['status'] == "Compliant")
    partial = sum(1 for r in results if r['status'] == "Partially Compliant")
    not_compliant = sum(1 for r in results if r['status'] == "Not Compliant")

    compliance_pct = round((compliant / total) * 100, 2) if total else 0

    total_weight = sum(r['weight'] for r in results)
    achieved_weight = sum(r['weighted_score'] for r in results)
    weighted_compliance = round((achieved_weight / total_weight) * 100, 2)

    print("\n📊 Compliance Summary")
    print(f"  Total Controls Evaluated: {total}")
    print(f"  Compliant: {compliant}")
    print(f"  Partially Compliant: {partial}")
    print(f"  Not Compliant: {not_compliant}")
    print(f"  Compliance Percentage: {compliance_pct}%")
    print(f"  Weighted Compliance (Risk-Based): {weighted_compliance}%")

    print(f"\n📁 Saved: {results_path}")
    print(f"📁 Saved: {gaps_path}")


if __name__ == "__main__":
    main()

