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

class SpecificProdNotFoundInputSchema(BaseIOSchema):
    """ ProductSepcificRAGInputSchema """
    query: str = Field(None, description="The user's query.")
    products: List[SephoraProductViewModel] = Field(None, description="The product found in the SQL search.")
    reviews: List[SephoraReviewViewModel] = Field(None, description="The reviews found in the semantic search.")

class SpecificProdNotFoundOutputSchema(BaseIOSchema):
    """ SpecificProdNotFoundOutputSchema """
    response: str = Field(None, description="The answer to the user query.")

prompt = SystemPromptGenerator(
    background=[
        "You are a helpful AI assistant specialized in beauty and skincare products from Sephora.",
        "The user has asked about a specific product, but it was not found in the database.",
        "You have access to similar products and their reviews, which you can use to provide a helpful response.",
        "Inform the user that the specific product they mentioned was not found, but you can provide information based on similar products and reviews.",
    ],
    steps=[
        "Check if the product is present. If not, acknowledge the missing product.",
        "Review the provided reviews and product information to identify relevant insights.",
        "Summarize the sentiment and key opinions from these reviews that may still help answer the user's query.",
        "Offer helpful guidance or suggestions based on similar products, without making assumptions about the missing one.",
    ],
    output_instructions=[
        "Begin by politely noting that the specific product was not found.",
        "Follow up with insights or advice based on the available reviews.",
        "Avoid hallucinating specific details about the missing product.",
        "Use clear, friendly, and concise language tailored to a consumer audience.",
    ]
)

specific_prod_not_found_rag_worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        temperature=0,
        input_schema=SpecificProdNotFoundInputSchema,
        output_schema=SpecificProdNotFoundOutputSchema,
        system_prompt_generator=prompt,
    ),
)

