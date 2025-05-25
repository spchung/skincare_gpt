from pprint import pprint
from app.lang_graphs.chat_v1.handlers.intents.follow_up_question.workers.follow_up_rewrite_worker import (
    follow_up_rewrite_worker,
    FollowUpRewriteInputSchema
)

prev_user_query = "What is the best sunscreen for oily skin?"
prev_ai_response = "I recommend the La Roche-Posay Anthelios Clear Skin Dry Touch Sunscreen SPF 60 for oily skin. It's lightweight and non-comedogenic."
follow_up_query = "Can you tell me more about its ingredients and how it feels on the skin?"

payload = FollowUpRewriteInputSchema(
    prev_user_query=prev_user_query,
    prev_ai_response=prev_ai_response,
    follow_up_query=follow_up_query
)

res = follow_up_rewrite_worker.run(payload)
rewritten_query = res.rewritten_query

print(f"Rewritten query: {rewritten_query}")