from tools.query_data import query_data

# ── CLI test ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json, sys
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Top 3 movies by worldwide gross"
    out = query_data(question)
    print(json.dumps(out, indent=2, default=str))
