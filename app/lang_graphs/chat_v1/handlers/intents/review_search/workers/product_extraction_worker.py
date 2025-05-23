import instructor
from typing import List
from pydantic import Field
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from app.models.sephora import SephoraProductViewModel, SephoraReviewViewModel
from app.internal.client import llm
from pydantic import Field

class InputExtractionInputSchema(BaseIOSchema):
    """ InputExtractionInputSchema """
    query: str = Field(None, description="The user's query.")

class InputExtractionOutputSchema(BaseIOSchema):
    """ InputExtractionOutputSchema """
    is_product_specific: bool = Field(None, description="Whether the query is product specific.")
    product_name: str | None = Field(None, description="The name of the product.")
    product_id: str | None = Field(None, description="The ID of the product.")
    brand_name: str | None = Field(None, description="The name of the brand.")

prompt = SystemPromptGenerator(
    background=[
        "You are an intelligent agent tasked with analyzing user queries to determine whether they refer to a specific skincare product.",
        "A query is considered product-specific if it clearly mentions both a product name (e.g., 'Hydrating Cleanser') and, optionally, a brand name (e.g., 'CeraVe').",
        "You have access to a product catalog and should try to match the query against known products and brands."
    ],
    steps=[
        "Check if the query mentions a specific product name and optionally a brand name.",
        "If both are mentioned, set 'is_product_specific' to True.",
        "If the query refers to product categories or is generic, set 'is_product_specific' to False.",
        "Attempt to extract the product name and brand name from the query, if available.",
        "Use the extracted names to look up the corresponding product ID in the catalog (if accessible)."
    ],
    output_instructions=[
        "Return 'is_product_specific' as True or False based on whether the query clearly references a specific product.",
        "If True, also return the extracted 'product_name', 'brand_name', and 'product_id' (if it can be found).",
        "If False, leave 'product_name', 'brand_name', and 'product_id' as None."
    ]
)

product_extraction_worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        temperature=0,
        input_schema=InputExtractionInputSchema,
        output_schema=InputExtractionOutputSchema,
        system_prompt_generator=prompt,
    ),
)
