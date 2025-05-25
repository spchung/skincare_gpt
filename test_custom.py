from pprint import pprint
from app.lang_graphs.chat_v1.handlers.intents.review_search.review_search import review_search_chain
from app.lang_graphs.chat_v1.handlers.intent_classification import (
    worker as intent_classification_worker,
    IntentClassificationInputSchema,
)

follow_up_test_cases = [
    {
        "previous_query": "What are the best face cleansers for dry skin?",
        "query": "Which of these is the most affordable?"
    },
    {
        "previous_query": "Can you recommend a sunscreen for oily skin?",
        "query": "What about fragrance-free options only?"
    },
    {
        "previous_query": "Suggest a moisturizer for sensitive skin.",
        "query": "How does that compare to Cetaphil?"
    },
    {
        "previous_query": "What do people think of La Roche-Posay cleansers?",
        "query": "Any mention of allergic reactions in the reviews?"
    },
    {
        "previous_query": "I need a serum for hyperpigmentation.",
        "query": "Does it contain niacinamide?"
    },
    {
        "previous_query": "Which eye creams are good for dark circles?",
        "query": "What about puffiness?"
    },
    {
        "previous_query": "List top 5 exfoliators for dry skin.",
        "query": "Can you sort them by price?"
    },
    {
        "previous_query": "Recommend a good cleanser for acne-prone skin.",
        "query": "Does Neutrogena have one like that?"
    }
]

if __name__ == '__main__':
    for test_case in follow_up_test_cases:
        print(f"Prev: {test_case['previous_query']}")
        print(f"Curr: {test_case['query']}")

        res = intent_classification_worker.run(IntentClassificationInputSchema(
            query=test_case['query'],
            previous_query=test_case['previous_query']
        ))
        print(f"Intent: {res.intent}")
        print("-" * 40)
