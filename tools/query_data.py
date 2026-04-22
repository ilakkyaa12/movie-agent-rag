import pandas as pd

# 🔹 Load CSV once
df = pd.read_csv("data/movies.csv")

# 🔹 Normalize movie column (important)
df["movie"] = df["movie"].str.lower()


# 🔥 STEP 1: Intent Detection (lightweight semantic layer)
def detect_intent(query: str):
    query = query.lower()

    if any(x in query for x in [
        "gross", "earning", "revenue", "box office", "highest gross", "top gross"
    ]):
        return "highest_gross"

    elif any(x in query for x in [
        "low budget", "lowest budget", "cheap", "least budget"
    ]):
        return "lowest_budget"

    elif any(x in query for x in [
        "rating", "rotten tomatoes", "best rated", "top rated"
    ]):
        return "best_rated"

    elif "after" in query:
        return "after_year"

    else:
        return "movie_lookup"


# 🔥 STEP 2: Main Query Function
def query_data(query: str):
    query = query.lower()
    intent = detect_intent(query)

    # 🔹 Highest grossing movies
    if intent == "highest_gross":
        result = df.sort_values(by="worldwide_gross", ascending=False).head(5)
        return result.to_dict(orient="records")

    # 🔹 Lowest budget movies
    elif intent == "lowest_budget":
        result = df.sort_values(by="budget", ascending=True).head(5)
        return result.to_dict(orient="records")

    # 🔹 Best rated movies
    elif intent == "best_rated":
        result = df.sort_values(by="rotten_tomatoes", ascending=False).head(5)
        return result.to_dict(orient="records")

    # 🔹 Movies after a given year
    elif intent == "after_year":
        try:
            year = int([word for word in query.split() if word.isdigit()][0])
            result = df[df["year"] > year]
            return result.to_dict(orient="records")
        except:
            return {"error": "Could not parse year"}

    # 🔹 Specific movie lookup
    elif intent == "movie_lookup":
        for movie in df["movie"]:
            if movie in query:
                result = df[df["movie"] == movie]
                return result.to_dict(orient="records")

        return {"error": "Movie not found"}

    return {"error": "Query not understood"}