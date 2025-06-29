import instructor
from typing import List
from pydantic import Field
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from app.models.sephora import SephoraProductViewModel, SephoraReviewViewModel
from app.internal.client import llm

class ReviewSearchRAGInputSchema(BaseIOSchema):
    """ ReviewSearchRAGInputSchema """
    query: str = Field(None, description="The user's query.")
    reviews: List[dict] = Field(None, description="The reviews found in the semantic search.")
    products: List[dict] = Field(None, description="The products found in the SQL search.")

class ReviewSearchRAGOutputSchema(BaseIOSchema):
    """ ReviewSearchRAGOutputSchema """
    response: str = Field(None, description="The response to the user's query.")

prompt = SystemPromptGenerator(
    background=[
        "You are an expert skincare assistant designed to help users understand how others feel about beauty products.",
        "You are provided with a list of relevant reviews and product details based on the user's query.",
        "Your goal is to summarize or extract opinions from the reviews to help the user make an informed decision.",
    ],
    steps=[
        "Carefully read the user's query to determine what information they are seeking (e.g., effectiveness, side effects, suitability for certain skin types).",
        "Review the list of matching reviews for sentiment, experiences, and recurring themes related to the query.",
        "If product information is available, consider it as helpful context for understanding the reviews (e.g., ingredients, claims, pricing).",
        "Prioritize reviews that mention the user's likely concerns (e.g., skin tone, skin type, or the problem they are targeting).",
        "Summarize key insights from the reviews clearly and concisely. Highlight any common pros or cons users mention.",
    ],
    output_instructions=[
        "Provide a helpful and specific answer to the user's query, backed by the content of the reviews.",
        "Avoid speculation—only reference information contained in the reviews or product details.",
        "If reviews are insufficient or conflicting, state that clearly and advise accordingly.",
    ]
)

review_search_rag_worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        input_schema=ReviewSearchRAGInputSchema,
        output_schema=ReviewSearchRAGOutputSchema,
        system_prompt_generator=prompt,
    ),
)
