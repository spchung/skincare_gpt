import pytest
from app.lang_graphs.chat_v1.handlers.intent_classification import worker as intent_classification_worker
from app.lang_graphs.chat_v1.handlers.intent_classification import IntentClassificationInputSchema

product_search_queries = [
    "What are the best face cleansers for dry skin?",
    "Can you recommend a sunscreen for oily skin?",
    "Suggest a moisturizer for sensitive skin.",
    "I need a serum for hyperpigmentation.",
    "Which eye creams are good for dark circles?",
    "List top 5 exfoliators for dry skin.",
    "Recommend a good cleanser for acne-prone skin."
]

@pytest.mark.parametrize("query", product_search_queries)
def test_product_intent(query):
    res = intent_classification_worker.run(IntentClassificationInputSchema(
        query=query,
        previous_query=None
    ))
    assert res.intent == "product_search"


review_search_queries = [
    "What are the reviews for the latest sunscreen?",
    "Can you show me reviews for the new moisturizer?",
    "I want to see customer feedback on the new serum.",
    "What do people say about the new eye cream?",
    "Are there any reviews for the latest exfoliator?"
    "Can you find reviews for the 7 Day Face Scrub Cream Rinse-Off Formula?",
]
@pytest.mark.parametrize("query", review_search_queries)
def test_review_intent(query):
    res = intent_classification_worker.run(IntentClassificationInputSchema(
        query=query,
        previous_query=None
    ))
    assert res.intent == "review_search"


# brand, purpose, price, ingredient, or SPF
filter_search_queries = [
    "What are the best products from CLINIQUE?",
    "What are my options for anit-aging products under $50?",
    "What are the best products with SPF 30 or higher?",
    "Find me products with hyaluronic acid under $50.",
    "What are the best products for acne with salicylic acid?",
    "Show me products with vitamin C. for dry skin",
    "What are the best products for oily skin with niacinamide?",
]

@pytest.mark.parametrize("query", filter_search_queries)
def test_filter_intent(query):
    res = intent_classification_worker.run(IntentClassificationInputSchema(
        query=query,
        previous_query=None
    ))
    assert res.intent == "filter_search"


other_queries = [
    "What is the weather like today?",
    "Tell me a joke.",
    "How do I reset my password?",
    "What is the capital of France?",
    "Can you help me with my homework?",
]

@pytest.mark.parametrize("query", other_queries)
def test_other_intent(query):
    res = intent_classification_worker.run(IntentClassificationInputSchema(
        query=query,
        previous_query=None
    ))
    assert res.intent == "other"

follow_up_query_pairs = [
    ("What are the best face cleansers for dry skin?", "Which of these is the most affordable?"),
    ("Can you recommend a sunscreen for oily skin?", "What about fragrance-free options only?"),
    ("Suggest a moisturizer for sensitive skin.", "How does that compare to Cetaphil?"),
    ("What do people think of La Roche-Posay cleansers?", "Any mention of allergic reactions in the reviews?"),
    ("I need a serum for hyperpigmentation.", "Does it contain niacinamide?"),
    ("Which eye creams are good for dark circles?", "What about puffiness?"),
    ("List top 5 exfoliators for dry skin.", "Can you sort them by price?"),
    ("Recommend a good cleanser for acne-prone skin.", "Does Neutrogena have one like that?"),
    ("What’s a good body lotion for winter?", "Does it work for eczema too?"),
    ("Are there any night creams for anti-aging?", "Is retinol included in those?")
]
@pytest.mark.parametrize("previous_query, query", follow_up_query_pairs)
def test_follow_up_intent(previous_query, query):
    res = intent_classification_worker.run(IntentClassificationInputSchema(
        query=query,
        previous_query=previous_query
    ))
    assert res.intent == "follow_up"    