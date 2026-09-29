"""Live submission rows for kaggriculture, read fresh from the API (no cached CSV)."""
import sys

from kaggle.api.kaggle_api_extended import KaggleApi


def main():
    api = KaggleApi()
    api.authenticate()
    rows = api.competition_submissions("kaggriculture")
    for s in rows[:12]:
        d = s.to_dict() if hasattr(s, "to_dict") else vars(s)
        print({k: d.get(k) for k in ("ref", "date", "status", "publicScore", "description", "fileName")})
    print("TOTAL_ROWS", len(rows))
    lim = api.competition_get_submission_limits("kaggriculture")
    print("LIMITS", lim)
    return 0


if __name__ == "__main__":
    sys.exit(main())
