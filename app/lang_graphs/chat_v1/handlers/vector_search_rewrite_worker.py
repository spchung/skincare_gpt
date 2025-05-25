
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from pydantic import Field  
from app.internal.client import llm
import instructor

class QueryRewriteInputSchema(BaseIOSchema):
    """QueryRewriteInputSchema"""
    query: str = Field(..., description="The original user query to be rewritten for semantic retrieval.")

# Output schema
class QueryRewriteOutputSchema(BaseIOSchema):
    """QueryRewriteOutputSchema"""
    rewritten_query: str = Field(..., description="A concise, neutral, and retrieval-optimized version of the original query.")


prompt = SystemPromptGenerator(
    background=[
        "You are a query rewriting assistant in a skincare-focused search system.",
        "Your job is to transform a user’s natural-language query into a concise, self-contained, and semantically neutral form suitable for document retrieval.",
        "Your rewritten query should preserve the user’s intent but improve its effectiveness when used in a semantic search engine.",
        "Avoid emotional, ambiguous, or overly general language. Clarify negations and make implicit needs explicit."
    ],
    steps=[
        "Read the user’s original query carefully.",
        "Reword the query into a clear, factual, and retrieval-friendly version.",
        "Avoid vague phrases like 'that doesn't hurt' or 'feels good' — instead, specify the condition or desired properties.",
        "Use neutral phrasing — avoid negation that can confuse semantic similarity models.",
        "Do not add new information. Just clarify or structure what's already there."
    ],
    output_instructions=[
        "Output only the rewritten query, without any additional text or explanation.",
        "Ensure the output is concise, neutral, and preserves the core meaning of the original."
    ]
)

vector_search_rewrite_agent = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        temperature=0,
        input_schema=QueryRewriteInputSchema,
        output_schema=QueryRewriteOutputSchema,
        system_prompt_generator=prompt,
    )
)
