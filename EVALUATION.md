# 📊 Evaluation

## 🎯 Goal

Evaluate how well the agent:

- Selects the correct tool
- Combines multiple sources
- Produces grounded answers
- Avoids hallucination
- Handles failure cases

---

# Test Cases 1

Question: What is the worldwide gross of Inception?

  [Step 1] Tool: query_data | Input: {'question': 'movies.csv — Inception, worldwide_gross'}

Answer: According to the structured CSV data, the worldwide gross of Inception is $836 million.


# Test Cases 2

Question: Why did Avengers Endgame earn more than Inception and what do critics say about both films?

  [Step 1] Tool: query_data | Input: {'question': 'box-office numbers for Avengers Endgame and Inception'}
  [Step 2] Tool: search_docs | Input: {'query': 'opinions on Avengers Endgame and Inception'}
  [Step 3] Tool: query_data | Input: {'question': 'box-office numbers for Avengers Endgame'}
  [Step 4] Tool: web_search | Input: {'query': 'Avengers Endgame box office gross'}

Answer: 

Avengers Endgame earned more than Inception at the global box office, with a total gross of over $2.79 billion compared to Inception's $825 million. Critics praised both films, but the exact page numbers from search_docs are unavailable.

# Test Cases 3

Question: Is Parasite worth watching based on reviews and how did it perform at the box office?

[Step 1] Tool: search_docs | Input: {'query': 'Parasite reviews'}
[Step 2] Tool: query_data | Input: {'question': 'Parasite box office performance'}

Answer: 

It seems that Parasite has received widespread critical acclaim for its thought-provoking exploration of class inequality, its ability to balance entertainment with thematic depth, and its masterful direction. The film's unique blend of dark humor, satire, and social commentary has resonated with many critics, with some even considering it one of the best films of its year.

In terms of its box office performance, Parasite was a commercial success, grossing over $262 million worldwide, with a domestic total of $26.2 million. Notably, it received a 99% approval rating on Rotten Tomatoes.

Given the film's critical and commercial success, I would highly recommend watching Parasite!

 # Test Cases 4

Question: What is the box office of Top Gun Maverick, what do critics say about it, and find the latest 2024 or 2025 news about it from the web?

[Step 1] Tool: query_data | Input: {'question': 'Top Gun Maverick, worldwide_gross'}
  [Step 2] Tool: search_docs | Input: {'query': 'Top Gun Maverick, critic reviews'}
  [Step 3] Tool: web_search | Input: {'query': 'Top Gun Maverick, latest news 2024'}

Answer: Based on the results,

Top Gun Maverick's worldwide gross is 1,495,000,000, according to (movies.csv — Top Gun Maverick, worldwide_gross).

Critics praise Top Gun Maverick for its (top_gun, inception.txt) and (top_gun, critic reviews). According to (top_gun, critic reviews), critics (top_gun) and (top_gun). The film's (top_gun, Critical Analysis) concludes that it is a compelling sequel that delivers both spectacle and emotional depth, honoring its predecessor while standing strong as a modern action film.

Recently, Top Gun Maverick was featured in (https://www.youtube.com/watch?v=OKshN0dUaUk, published unknown), where Tom Cruise confirmed the third installment is happening. Another article on (https://www.imdb.com/news/ni65799872/, published unknown) revealed the news about Top Gun 3. Additionally, (https://www.rollingstone.com/tv-movie-news/top-gun-3-tom-cruise-confirmed-1235548433/, published unknown) confirmed Tom Cruise's return for the third sequel to Top Gun.

# Test Cases 5

Question: Compare the box office, critic reviews, and latest news for Inception, Interstellar, The Dark Knight, and Oppenheimer


  [Step 1] Tool: query_data | Input: {'question': 'box office - Inception, Interstellar, The Dark Knight, Oppenheimer'}
  [Step 2] Tool: query_data | Input: {'question': 'budget - Inception, Interstellar, The Dark Knight, Oppenheimer'}
  [Step 3] Tool: query_data | Input: {'question': 'RT score - Inception, Interstellar, The Dark Knight, Oppenheimer'}
  [Step 4] Tool: search_docs | Input: {'query': 'Inception'}
  [Step 5] Tool: search_docs | Input: {'query': 'Interstellar'}
  [Step 6] Tool: search_docs | Input: {'query': 'The Dark Knight'}
  [Step 7] Tool: search_docs | Input: {'query': 'Oppenheimer'}
  [Step 8] Tool: web_search | Input: {'query': 'Inception latest news'}

Answer: I was unable to reach a confident answer within the 8-step tool call limit. The tools I called did not return sufficient information to answer your question. Please try rephrasing with a more specific movie title or question.