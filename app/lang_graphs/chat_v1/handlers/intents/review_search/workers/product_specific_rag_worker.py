'''
This agent extracnt the a product from the context using extracted bits of product info from the query
'''
import instructor
from typing import List
from pydantic import Field
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from app.models.sephora import SephoraProductViewModel, SephoraReviewViewModel
from app.internal.client import llm
from pydantic import Field

class ProductSpecificRAGInputSchema(BaseIOSchema):
    """ ProductSepcificRAGInputSchema """
    query: str = Field(None, description="The user's query.")
    product: SephoraProductViewModel = Field(None, description="The product found in the SQL search.")
    reviews: List[SephoraReviewViewModel] = Field(None, description="The reviews found in the semantic search.")

class ProductSpecificRAGOutputSchema(BaseIOSchema):
    """ ProductSpecificRAGOutputSchema """
    answer: str = Field(None, description="The answer to the user query.")

prompt = SystemPromptGenerator(
    background=[
        "You are a helpful AI assistant specialized in beauty and skincare products from Sephora.",
        "You are provided with a user query, a product that was found through an SQL search, and relevant reviews retrieved using semantic search.",
        "Your goal is to extract relevant information from the query and respond based on the context of the provided product and its reviews."
    ],
    steps=[
        "Identify the specific product mentioned in the user's query or confirm if the provided product context is relevant.",
        "Determine the user's intent—are they asking about product usage, ingredients, skin type compatibility, effectiveness, comparison, or general review?",
        "Use the product information to answer fact-based queries (e.g., ingredients, brand, product type).",
        "Use the reviews to answer experiential or opinion-based queries (e.g., does it work well for dry skin? what do users say about it?).",
        "If the query references something not covered in the product or reviews, acknowledge the gap and clarify if needed."
    ],
    output_instructions=[
        "Provide a concise, accurate, and helpful response based on the available product and review data.",
        "Avoid fabricating information. If something is unknown or not provided in the context, say so.",
        "Format the response as a complete sentence or paragraph, suitable for display in a user-facing application."
    ]
)

product_specific_rag_worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        temperature=0,
        input_schema=ProductSpecificRAGInputSchema,
        output_schema=ProductSpecificRAGOutputSchema,
        system_prompt_generator=prompt,
    ),
)

