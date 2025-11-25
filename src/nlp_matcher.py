# src/nlp_matcher.py
from difflib import SequenceMatcher

def similarity(a: str, b: str) -> float:
    """Return similarity ratio between two strings (0–100)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

def best_policy_match(control_text: str, policies: dict):
    """
    Given control description and dict of {filename: text},
    return the best matching policy and similarity score.
    """
    best_match = None
    best_score = 0

    for name, text in policies.items():
        score = similarity(control_text, text)
        if score > best_score:
            best_score = score
            best_match = name

    return best_match, round(best_score, 2)

if __name__ == "__main__":
    # simple test
    sample_control = "Management direction for information security"
    sample_policies = {
        "acceptable_use.txt": "This policy covers acceptable use of information systems...",
        "data_protection.txt": "This policy describes handling of personal data..."
    }

    match, score = best_policy_match(sample_control, sample_policies)
    print(f"Best match: {match} (score: {score})")
