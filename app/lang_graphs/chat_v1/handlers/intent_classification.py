from pydantic import Field
import instructor
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from app.lang_graphs.chat_v1.models.state import State
from app.internal.client import llm

class IntentClassificationInputSchema(BaseIOSchema):
    """ IntentClassificationInputSchema """
    query: str = Field(None, description="The user's query.")

class IntentClassificationOutputSchema(BaseIOSchema):
    """ IntentClassificationOutputSchema """
    intent: str =Field(None, description="The intent of the user's query.")

prompt = SystemPromptGenerator(
    background=[
        'You are an AI assistant responsible for understanding user queries in a skincare chatbot.',
        'You are tasked with identifying the user’s intent from their query.',
        'The intent should be one of the predefined categories used to route the query to the correct module.'
    ],
    steps=[
        'Carefully read and understand the user’s query.',
        'Determine which of the following best describes the user’s intent:',
        '- product_search: when the user is looking for a skincare product for a condition or need.',
        '- review_search: when the user wants to know opinions or reviews about a product.',
        '- compare: when the user wants a comparison between two or more products.',
        '- filter_search: when the user includes constraints such as brand, purpose, price, ingredient, or SPF',
        '- other: if the query doesn’t fit any of the above.',
        'Return only the label that best matches the user’s intent.'
    ],
    output_instructions=[
        'Output only a single label: product_search, review_search, compare, filter_search, or other.',
        'Do not include explanations or full sentences.'
    ]
)

worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        temperature=0,
        input_schema=IntentClassificationInputSchema,
        output_schema=IntentClassificationOutputSchema,
        system_prompt_generator=prompt,
    ),
)

def intent_classification_router(state: State):
    res = worker.run(IntentClassificationInputSchema(query=state['messages'][-1].content))
    return { "intent": res.intent }
