
Define Intents (User Entry Points)
Design the chatbot to detect common user intents like:

Product Search: “Recommend me a sunscreen for oily skin”
product_search -> embed query, search product collection, get json from relational -> llm rewrite

Review Search: “What do people say about XYZ cream?”
review_search -> embed query, lookup review embeddings, get json from relational -> llm rewrite

Comparison: “Which is better: Product A or Product B?”
compare -> Retrieve both products, show key features

Constraint-based Filters: “Show me moisturizers under $30 with SPF”
filter_search -> Parse constraints, filter before embedding

======
graph LR
A(User Query) --> B(Intent Classifier)
B --> C1[Product Search]
B --> C2[Review Search]
B --> C3[Compare]

C1 --> D1[Embed Query -> Product Vector Store -> Top-k Results]
C2 --> D2[Embed Query -> Review Vector Store -> Top-k Reviews]
C3 --> D3[Retrieve Both Products -> Structured Comparison]

D1 & D2 & D3 --> E[LLM: Generate Final Answer]
E --> F(Chatbot Response)


