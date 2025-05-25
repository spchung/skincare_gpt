
from app.lang_graphs.chat_v1.graph_state import MainGraphState
from .workers.follow_up_rewrite_worker import follow_up_rewrite_worker, FollowUpRewriteInputSchema
from .workers.follow_up_rag_worker import FollowUpRagResInputSchema, follow_up_rag_worker
from app.internal.redis import RedisClient
from langchain_core.messages import AIMessage

def follow_up_question_handler(state: MainGraphState):
    '''
    steps 
     - prev + current query rewrite
     - fetch context + previous response
     - RAG 
    '''
    thread_id = state['thread_id']

    # 1. rewrite worker
    prev_user_query = state['messages'][-3].content if len(state['messages']) > 2 else ""
    prev_ai_response = state['messages'][-2].content if len(state['messages']) > 1 else ""
    follow_up_query = state['messages'][-1].content

    payload = FollowUpRewriteInputSchema(
        prev_user_query=prev_user_query,
        prev_ai_response=prev_ai_response,
        follow_up_query=follow_up_query
    )
    res = follow_up_rewrite_worker.run(payload)
    rewritten_query = res.rewritten_query

    # 2 format context (use redis last 5)
    r_client = RedisClient()
    context_array = r_client.get(f"entities:{thread_id}")

    # 3. RAG worker
    rag_payload = FollowUpRagResInputSchema(
        query=rewritten_query,
        prev_ai_response=prev_ai_response,
        entities=context_array if context_array else []
    )
    rag_res = follow_up_rag_worker.run(rag_payload)
    response = rag_res.response

    return {
        "messages": [AIMessage(content=response)],
        'intent': 'follow_up_question',
    }