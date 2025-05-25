import instructor
from typing import List
from pydantic import Field  
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from app.internal.client import llm

class FollowUpRagResInputSchema(BaseIOSchema):
    """ FollowUpRagResInputSchema """
    query: str = Field(None, description="The user's query.")
    entities: List[dict]

class FollowUpRagResOutputSchema(BaseIOSchema):
    """ FollowUpRagResOutputSchema """
    response: str = Field(None, description="The response to the user's query.")

prompt = SystemPromptGenerator(
    background=[

    ],
    steps=[
        
    ],
    output_instructions=[
        
    ]
)
worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        input_schema=FollowUpRagResInputSchema,
        output_schema=FollowUpRagResOutputSchema,
        system_prompt_generator=prompt,
    ),
)