from pydantic import Field
import instructor
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from app.lang_graphs.chat.graph_state import MainGraphState
from app.internal.client import llm
from typing import Optional
from langchain_core.messages import HumanMessage

class IntentClassificationInputSchema(BaseIOSchema):
    """ IntentClassificationInputSchema """
    query: str = Field(..., description="The user's query.")
    previous_query: Optional[str] = Field(None, description="The previous user query, if available. This helps in determining if the current query is a follow_up.")

class IntentClassificationOutputSchema(BaseIOSchema):
    """ IntentClassificationOutputSchema """
    intent: str = Field(..., description="The intent of the user's query.")

prompt = SystemPromptGenerator(
    background=[
        "You are an AI assistant responsible for understanding user queries in a skincare chatbot.",
        "You are tasked with identifying the user’s intent from their query.",
        "The intent should be one of the predefined categories used to route the query to the correct module.",
        "You are given the current user message and an optional list of previous messages (chat history), which includes both prior user queries and assistant responses."
    ],
    steps=[
        "Carefully read and understand the current user query.",
        "If previous_query is provided, examine it to understand the conversation context.",
        "IMPORTANT: The 'follow_up' intent should ONLY be used in very specific circumstances:",
        "- The current query uses demonstrative pronouns like 'this', 'that', 'these', 'those' referring to something from the previous query",
        "- The current query uses phrases like 'tell me more about it', 'what about that one', 'more details on this'",
        "- The current query is asking for clarification about a specific response (e.g., 'what do you mean by...', 'can you explain...')",
        "- The current query explicitly references something mentioned in the previous exchange (e.g., 'the product you mentioned', 'that ingredient you talked about')",
        "",
        "DO NOT classify as 'follow_up' if:",
        "- The query is a completely new skincare question, even if it's the second message",
        "- The query mentions different products, ingredients, or skin concerns than the previous query",
        "- The query can be understood and answered independently without the previous context",
        "- The query is a general greeting, thank you, or conversational response",
        "",
        "Use the following intent labels:",
        "- follow_up: ONLY when the current query explicitly depends on and cannot be understood without the previous conversation context",
        "- product_search: when the user is looking for a skincare product for a condition or need",
        "- review_search: when the user wants to know opinions or reviews about a product",
        "- filter_search: when the user includes specific constraints such as brand, purpose, price, ingredient, or SPF",
        "- other: if the query doesn't fit any of the above"
    ],
    output_instructions=[
        "Output only a single label: follow_up, product_search, review_search, filter_search, or other.",
        "Do not include explanations, just return the label."
    ]
)

worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        model_api_parameters={
            "temperature": 0,
            "max_tokens": 100,
        },
        input_schema=IntentClassificationInputSchema,
        output_schema=IntentClassificationOutputSchema,
        system_prompt_generator=prompt,
    ),
)

def intent_classification_router(state: MainGraphState):
    user_messages = [msg for msg in state['messages'] if isinstance(msg, HumanMessage)]
    query = user_messages[-1]
    previous_query = user_messages[-2] if len(user_messages) > 1 else None
    
    res = worker.run(IntentClassificationInputSchema(
        query=query.content,
        previous_query=previous_query.content if previous_query else None,
    ))

    print(f"INTENT: {res}")
    return { "intent": res.intent }
