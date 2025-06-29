import instructor
from typing import List
from pydantic import Field  
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from app.internal.client import llm

class FollowUpRagResInputSchema(BaseIOSchema):
    """ FollowUpRagResInputSchema """
    query: str = Field(None, description="The user's query.")
    prev_ai_response: str = Field(None, description="The AI assistant's response to the previous query.")
    entities: List[dict]

class FollowUpRagResOutputSchema(BaseIOSchema):
    """ FollowUpRagResOutputSchema """
    response: str = Field(None, description="The response to the user's query.")

prompt = SystemPromptGenerator(
    background=[
        "You are an AI assistant helping users with skincare-related queries.",
        "You are provided with:",
        "- A rewritten user query that is self-contained.",
        "- A list of entities (products or reviews) extracted from earlier messages.",
        "- The previous AI assistant response, which may contain context or explanations the user is following up on.",
        "Use this context to answer the user’s current query as accurately and helpfully as possible."
    ],
    steps=[
        "Carefully read the rewritten user query.",
        "Review the entities list — these represent relevant products or reviews from earlier in the conversation.",
        "Review the previous AI assistant response — the current query may refer to something mentioned there.",
        "Use all provided context to answer the user's current query clearly and concisely.",
        "If the context (entities + previous response) is insufficient to answer the query confidently, acknowledge the lack of sufficient information and respond politely."
    ],
    output_instructions=[
        "Return only the final answer to the user’s current query.",
        "Use information from the provided context to support your response.",
        "Be concise but informative.",
        "If you cannot answer the query based on the given context, respond clearly that more information is needed."
    ]
)

follow_up_rag_worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        input_schema=FollowUpRagResInputSchema,
        output_schema=FollowUpRagResOutputSchema,
        system_prompt_generator=prompt,
    ),
)