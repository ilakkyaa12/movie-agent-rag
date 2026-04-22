from tools.search_docs import search_docs

queries = [
    "What is Parasite about?",
    "Themes in Oppenheimer",
    "Visual style of Oppenheimer"
]

for q in queries:
    print(f"\nQuery: {q}")
    results = search_docs(q)

    for i, r in enumerate(results):
        print(f"\nResult {i+1}:")
        print("Source:", r["source"])
        print("Content:", r["content"][:200])  # print first 200 chars
        print("-" * 50)