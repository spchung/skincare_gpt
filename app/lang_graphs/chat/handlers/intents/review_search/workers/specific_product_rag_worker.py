import instructor
from typing import List
from pydantic import Field
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from app.models.sephora import SephoraProductViewModel, SephoraReviewViewModel
from app.internal.client import llm

class SpecificProductRecuewRAGInputSchema(BaseIOSchema):
    """ SpecificProductRecuewRAGInputSchema """
    query: str = Field(None, description="The user's query.")
    reviews: List[SephoraReviewViewModel] = Field(None, description="The reviews found in the semantic search.")
    product: SephoraProductViewModel = Field(None, description="The product information in question.")

class SpecificProductRecuewRAGOutputSchema(BaseIOSchema):
    """ SpecificProductRecuewRAGOutputSchema """
    response: str = Field(None, description="The response to the user's query.")

prompt = SystemPromptGenerator(
    background=[
        "You are an expert skincare assistant designed to help users understand how others feel about beauty products.",
        "The user has requested information about a specific product and its reviews.",
        "Your goal is to summarize or extract opinions from the reviews to answer the user's query.",
    ],
    steps=[
        "Read and understand the user's query carefully to determine what kind of opinion or information they are seeking.",
        "Review the product information to understand the context (e.g., ingredients, product type, usage, etc.).",
        "Carefully read through the list of provided reviews.",
        "Identify patterns, sentiments, and specific opinions that relate directly to the user's query.",
        "Use a balanced tone—highlighting both positive and negative feedback when appropriate.",
    ],
    output_instructions=[
        "Respond with a concise, natural-sounding answer that directly addresses the user's query.",
        "Reference specific opinions or trends from the reviews, without quoting them verbatim unless they are particularly impactful.",
        "Do not include any information not found in the product description or reviews.",
        "Avoid generalizations; focus on what reviewers specifically said.",
        "Maintain a helpful, expert tone consistent with a knowledgeable skincare assistant."
    ]
)

specific_product_rag_worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        input_schema=SpecificProductRecuewRAGInputSchema,
        output_schema=SpecificProductRecuewRAGOutputSchema,
        system_prompt_generator=prompt,
    ),
)


# def specific_product_rag_worker_run(input_data: SpecificProductRecuewRAGInputSchema) -> SpecificProductRecuewRAGOutputSchema:
