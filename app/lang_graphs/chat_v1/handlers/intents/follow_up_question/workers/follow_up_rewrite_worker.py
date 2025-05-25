import instructor
from pydantic import Field  
from app.internal.client import llm
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase

class FollowUpRewriteInputSchema(BaseIOSchema):
    """Schema for rewriting a follow-up query into a standalone query."""
    prev_user_query: str = Field(..., description="The previous user query.")
    prev_ai_response: str = Field(..., description="The AI assistant's response to the previous query.")
    follow_up_query: str = Field(..., description="The current user query which follows up on the previous exchange.")

class FollowUpRewriteOutputSchema(BaseIOSchema):
    """Schema for the rewritten standalone query."""
    rewritten_query: str = Field(..., description="A fully self-contained version of the current query.")

rewrite_prompt = SystemPromptGenerator(
    background=[
        "You are an AI assistant that rewrites user follow-up questions into fully self-contained queries.",
        "You are given the previous user query, the assistant’s response to that query, and the current user follow-up message.",
        "Your job is to produce a rewritten query that includes all necessary context from the previous conversation so that it can be understood independently."
    ],
    steps=[
        "Read the previous user query carefully.",
        "Read the assistant's response — this might contain specific product names or facts the follow-up refers to.",
        "Read the follow-up query and identify what it refers to from the prior exchange.",
        "Rewrite the follow-up query so that it becomes a standalone, complete question, with all necessary context included."
        "Rewrite the follow-up query in the style of a user asking a direct, standalone question — not as an assistant paraphrasing."
    ],
    output_instructions=[
        "Return only the rewritten query as a plain string.",
        "Rewrite in a natural, user-like tone — avoid overly formal or assistant-style phrasing like 'Can you...'",
        "Prefer direct question forms like 'What are...', 'Which ones...', 'Does it...', etc.",
        "Be concise but ensure essential context is preserved.",
        "Do not include 'Rewritten query:' or any other extra text — just output the rewritten query."
    ]

)

follow_up_rewrite_worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        model_api_parameters={
            "temperature": 0
        },
        input_schema=FollowUpRewriteInputSchema,
        output_schema=FollowUpRewriteOutputSchema,
        system_prompt_generator=rewrite_prompt,
    ),
)