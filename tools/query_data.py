"""
query_data.py — Structured query tool for the movies CSV.

Use this tool when the question asks about numbers, rankings, comparisons,
box-office performance, budgets, grosses, scores, or any factual attribute
that lives in the structured movie dataset. Do NOT use this tool for opinions,
reviews, or narrative explanations — use search_docs for those.

Input  : a natural-language question about the movie data
Output : a dict with keys "result" (str), "rows" (list[dict]), "source" (str)
"""

from __future__ import annotations
import os
import re
import pandas as pd
from rapidfuzz import process, fuzz   # pip install rapidfuzz

# ── Path to CSV ────────────────────────────────────────────────────────────────
_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "movies.csv")

# ── Load once at import time ───────────────────────────────────────────────────
def _load() -> pd.DataFrame:
    df = pd.read_csv(_CSV_PATH)
    # Normalise column names: lowercase, underscores
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    # Attempt to coerce common numeric columns silently
    for col in df.columns:
        if df[col].dtype == object:
            cleaned = df[col].astype(str).str.replace(r"[\$,%]", "", regex=True).str.strip()
            converted = pd.to_numeric(cleaned, errors="coerce")
            # Only replace if most values converted successfully
            if converted.notna().mean() > 0.6:
                df[col] = converted
    return df

_DF: pd.DataFrame = _load()

# ── Column aliases: maps natural-language terms → actual column names ──────────
_COL_ALIASES = {
    "title":          ["title", "movie", "film", "name"],
    "budget":         ["budget", "cost", "production_budget", "production cost"],
    "gross":          ["gross", "revenue", "worldwide_gross", "total_gross",
                       "box_office", "earnings", "worldwide gross"],
    "opening":        ["opening", "opening_weekend", "opening weekend",
                       "domestic_opening", "opening_gross"],
    "rt_score":       ["rotten_tomatoes", "rt_score", "rt", "tomatometer",
                       "rotten tomatoes", "critic score", "critics score"],
    "audience_score": ["audience_score", "audience score", "popcornmeter",
                       "cinemascore", "audience"],
    "year":           ["year", "release_year", "released", "release year"],
    "director":       ["director", "directed by", "filmmaker"],
    "genre":          ["genre", "genres", "category"],
    "studio":         ["studio", "distributor", "production company"],
}

def _resolve_column(term: str) -> str | None:
    """Return the actual DataFrame column best matching a natural-language term."""
    term_l = term.lower().strip()
    if term_l in _DF.columns:
        return term_l
    for col, aliases in _COL_ALIASES.items():
        if term_l == col or any(term_l in a or a in term_l for a in aliases):
            if col in _DF.columns:
                return col
            for alias in aliases:
                if alias in _DF.columns:
                    return alias
            match, score, _ = process.extractOne(col, _DF.columns, scorer=fuzz.token_sort_ratio)
            if score >= 70:
                return match
    match, score, _ = process.extractOne(term_l, _DF.columns, scorer=fuzz.token_sort_ratio)
    if score >= 65:
        return match
    return None


def _fuzzy_find_movies(query_term: str, top_n: int = 5) -> pd.DataFrame:
    """Return rows whose title fuzzy-matches query_term."""
    title_col = _resolve_column("title") or "title"
    if title_col not in _DF.columns:
        return _DF.head(0)
    titles = _DF[title_col].astype(str).tolist()
    hits = process.extract(query_term, titles, scorer=fuzz.token_set_ratio, limit=top_n)
    matched_indices = [idx for _, score, idx in hits if score >= 55]
    return _DF.iloc[matched_indices].copy() if matched_indices else _DF.head(0)


# ── Intent patterns ────────────────────────────────────────────────────────────
# Each pattern: (regex, handler_fn)
# Handler receives the re.Match object + the full question string

def _handle_highest(m: re.Match, question: str) -> dict:
    col_term = m.group(1)
    col = _resolve_column(col_term)
    if col is None or not pd.api.types.is_numeric_dtype(_DF[col]):
        return _err(f"Could not find a numeric column matching '{col_term}'.")
    title_col = _resolve_column("title") or "title"
    row = _DF.loc[_DF[col].idxmax()]
    value = row[col]
    title = row.get(title_col, "N/A")
    return _ok(f"Highest {col}: {title} ({value})", [row.to_dict()])


def _handle_lowest(m: re.Match, question: str) -> dict:
    col_term = m.group(1)
    col = _resolve_column(col_term)
    if col is None or not pd.api.types.is_numeric_dtype(_DF[col]):
        return _err(f"Could not find a numeric column matching '{col_term}'.")
    title_col = _resolve_column("title") or "title"
    row = _DF.loc[_DF[col].idxmin()]
    value = row[col]
    title = row.get(title_col, "N/A")
    return _ok(f"Lowest {col}: {title} ({value})", [row.to_dict()])


def _handle_top_n(m: re.Match, question: str) -> dict:
    n = int(m.group(1))
    col_term = m.group(2)
    col = _resolve_column(col_term)
    if col is None or not pd.api.types.is_numeric_dtype(_DF[col]):
        return _err(f"No numeric column matching '{col_term}'.")
    title_col = _resolve_column("title") or "title"
    top = _DF.nlargest(n, col)[[title_col, col] if title_col in _DF.columns else [col]]
    result_str = f"Top {n} by {col}:\n" + "\n".join(
        f"  {i+1}. {row.get(title_col,'?')} — {row[col]}"
        for i, (_, row) in enumerate(top.iterrows())
    )
    return _ok(result_str, top.to_dict("records"))


def _handle_compare(m: re.Match, question: str) -> dict:
    """Compare two movies on any attribute."""
    movie_a = m.group(1).strip()
    movie_b = m.group(2).strip()
    rows_a = _fuzzy_find_movies(movie_a, top_n=1)
    rows_b = _fuzzy_find_movies(movie_b, top_n=1)
    if rows_a.empty or rows_b.empty:
        missing = movie_a if rows_a.empty else movie_b
        return _err(f"Could not find movie matching '{missing}' in the dataset.")
    row_a = rows_a.iloc[0]
    row_b = rows_b.iloc[0]
    title_col = _resolve_column("title") or "title"
    lines = [f"Comparison: {row_a.get(title_col,'?')} vs {row_b.get(title_col,'?')}"]
    for col in _DF.columns:
        if col == title_col:
            continue
        va, vb = row_a.get(col), row_b.get(col)
        if pd.notna(va) and pd.notna(vb):
            lines.append(f"  {col}: {va}  |  {vb}")
    return _ok("\n".join(lines), [row_a.to_dict(), row_b.to_dict()])


def _handle_lookup(m: re.Match, question: str) -> dict:
    """Look up a specific field for a named movie."""
    # group(1) = attribute term, group(2) = movie title
    col_term = m.group(1).strip()
    movie_term = m.group(2).strip()
    col = _resolve_column(col_term)
    rows = _fuzzy_find_movies(movie_term, top_n=1)
    if rows.empty:
        return _err(f"No movie matching '{movie_term}' found.")
    row = rows.iloc[0]
    if col and col in row.index:
        val = row[col]
        title_col = _resolve_column("title") or "title"
        return _ok(f"{row.get(title_col,'?')} — {col}: {val}", [row.to_dict()])
    # Return the full row if column not identified
    return _ok(str(row.to_dict()), [row.to_dict()])


def _handle_filter_genre(m: re.Match, question: str) -> dict:
    genre_term = m.group(1).strip()
    genre_col = _resolve_column("genre")
    if genre_col is None or genre_col not in _DF.columns:
        return _err("No genre column found in dataset.")
    mask = _DF[genre_col].astype(str).str.contains(genre_term, case=False, na=False)
    subset = _DF[mask]
    if subset.empty:
        return _err(f"No movies found with genre matching '{genre_term}'.")
    return _ok(f"Found {len(subset)} movies in genre '{genre_term}'.", subset.to_dict("records"))


def _handle_filter_year(m: re.Match, question: str) -> dict:
    year = int(m.group(1))
    year_col = _resolve_column("year")
    if year_col is None or year_col not in _DF.columns:
        return _err("No year column found in dataset.")
    subset = _DF[_DF[year_col] == year]
    if subset.empty:
        return _err(f"No movies found for year {year}.")
    return _ok(f"Movies in {year} ({len(subset)} found):", subset.to_dict("records"))


def _handle_average(m: re.Match, question: str) -> dict:
    col_term = m.group(1).strip()
    col = _resolve_column(col_term)
    if col is None or not pd.api.types.is_numeric_dtype(_DF[col]):
        return _err(f"Cannot compute average — no numeric column matching '{col_term}'.")
    avg = _DF[col].mean()
    return _ok(f"Average {col}: {avg:.2f}", [])


def _handle_count(m: re.Match, question: str) -> dict:
    return _ok(f"Total movies in dataset: {len(_DF)}", [])


def _handle_list_all(m: re.Match, question: str) -> dict:
    title_col = _resolve_column("title") or "title"
    titles = _DF[title_col].tolist() if title_col in _DF.columns else []
    return _ok("All movies:\n" + "\n".join(f"  - {t}" for t in titles), _DF.to_dict("records"))


def _handle_director_movies(m: re.Match, question: str) -> dict:
    director_name = m.group(1).strip()
    dir_col = _resolve_column("director")
    if dir_col is None or dir_col not in _DF.columns:
        return _err("No director column found in dataset.")
    mask = _DF[dir_col].astype(str).str.contains(director_name, case=False, na=False)
    subset = _DF[mask]
    if subset.empty:
        # Try fuzzy
        directors = _DF[dir_col].dropna().unique().tolist()
        match, score, _ = process.extractOne(director_name, [str(d) for d in directors], scorer=fuzz.token_set_ratio)
        if score >= 60:
            mask = _DF[dir_col].astype(str).str.contains(match, case=False, na=False)
            subset = _DF[mask]
    if subset.empty:
        return _err(f"No movies by director matching '{director_name}'.")
    title_col = _resolve_column("title") or "title"
    titles = subset[title_col].tolist() if title_col in subset.columns else []
    return _ok(f"Movies by '{director_name}': {titles}", subset.to_dict("records"))


# ── Intent routing table ───────────────────────────────────────────────────────
# Ordered: more specific patterns first
_INTENTS = [
    # top N by <col>
    (re.compile(r"top\s+(\d+)\s+(?:movies?\s+)?(?:by\s+)?(.+?)(?:\s*\?)?$", re.I), _handle_top_n),
    # highest / best <col>
    (re.compile(r"(?:highest|most|best|largest|biggest)\s+(.+?)(?:\s+movie|\s+film|\s*\?)?$", re.I), _handle_highest),
    # lowest / worst <col>
    (re.compile(r"(?:lowest|least|worst|smallest)\s+(.+?)(?:\s+movie|\s+film|\s*\?)?$", re.I), _handle_lowest),
    # compare X and Y / X vs Y
    (re.compile(r"compare\s+(.+?)\s+(?:and|vs\.?|versus)\s+(.+?)(?:\s*\?)?$", re.I), _handle_compare),
    (re.compile(r"(.+?)\s+(?:vs\.?|versus)\s+(.+?)(?:\s*\?)?$", re.I), _handle_compare),
    # <attr> of <movie>  |  what is the <attr> of <movie>
    (re.compile(r"(?:what\s+(?:is|was|were)\s+(?:the\s+)?)?([\w\s]+?)\s+of\s+(.+?)(?:\s*\?)?$", re.I), _handle_lookup),
    # movies in genre X
    (re.compile(r"(?:movies?|films?)\s+(?:in|from|of|with)\s+(?:genre\s+)?(.+?)(?:\s*\?)?$", re.I), _handle_filter_genre),
    # movies in year X
    (re.compile(r"(?:movies?|films?|released)\s+in\s+(\d{4})(?:\s*\?)?$", re.I), _handle_filter_year),
    # average <col>
    (re.compile(r"average\s+(.+?)(?:\s*\?)?$", re.I), _handle_average),
    # how many movies
    (re.compile(r"how\s+many\s+(?:movies?|films?|titles?)", re.I), _handle_count),
    # list all movies
    (re.compile(r"(?:list|show|display)\s+all\s+(?:movies?|films?|titles?)", re.I), _handle_list_all),
    # movies by director
    (re.compile(r"(?:movies?|films?)\s+(?:by|directed by|from)\s+(.+?)(?:\s*\?)?$", re.I), _handle_director_movies),
    # director's movies
    (re.compile(r"(.+?)(?:'s|s')?\s+movies?(?:\s*\?)?$", re.I), _handle_director_movies),
]


def _ok(result: str, rows: list[dict]) -> dict:
    return {"result": result, "rows": rows, "source": f"movies.csv ({len(rows)} row(s))", "error": None}


def _err(msg: str) -> dict:
    return {"result": None, "rows": [], "source": "movies.csv", "error": msg}


# ── Fallback: scan movie titles for any mention in question ───────────────────
def _fallback_title_scan(question: str) -> dict:
    """If no intent matched, try extracting a movie name from the question and returning its full row."""
    title_col = _resolve_column("title")
    if not title_col or title_col not in _DF.columns:
        return _err("No intent matched and no title column found.")
    # Extract the longest substring that fuzzy-matches a title
    words = question.split()
    best_rows = pd.DataFrame()
    best_score = 0
    for length in range(min(8, len(words)), 0, -1):
        for start in range(len(words) - length + 1):
            phrase = " ".join(words[start:start+length])
            rows = _fuzzy_find_movies(phrase, top_n=1)
            if not rows.empty:
                score = fuzz.token_set_ratio(phrase, rows.iloc[0][title_col])
                if score > best_score:
                    best_score = score
                    best_rows = rows
    if not best_rows.empty and best_score >= 55:
        row = best_rows.iloc[0]
        return _ok(f"Found movie: {row.to_dict()}", [row.to_dict()])
    return _err(f"Could not interpret query: '{question}'. Try asking about a specific movie title, director, or metric.")


# ── Public entry point ─────────────────────────────────────────────────────────
def query_data(question: str) -> dict:
    """
    Query the structured movies CSV using a natural-language question.

    This tool answers questions about box-office numbers, budgets, RT scores,
    audience scores, release years, directors, genres, and rankings. It uses a
    hybrid of rule-based intent matching and fuzzy string matching so that
    near-misses on movie titles and column names still resolve correctly.

    Args:
        question: A natural-language question about the movie data.
                  Examples:
                    "What was the worldwide gross of Inception?"
                    "Top 5 movies by RT score"
                    "Compare The Dark Knight and Interstellar"
                    "Movies directed by Christopher Nolan"
                    "Average budget"

    Returns:
        dict with keys:
            "result" (str | None)  — human-readable answer
            "rows"   (list[dict])  — raw matching rows
            "source" (str)         — attribution string
            "error"  (str | None)  — error message if lookup failed
    """
    q = question.strip()
    for pattern, handler in _INTENTS:
        m = pattern.search(q)
        if m:
            result = handler(m, q)
            if result["error"] is None:
                return result
            # If handler returned an error, don't stop — try next pattern
    # No intent produced a clean result; use fallback
    return _fallback_title_scan(q)
