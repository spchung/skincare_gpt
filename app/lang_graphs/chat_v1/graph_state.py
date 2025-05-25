from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from app.lang_graphs.chat_v1.models.basic_questioinaire import BasicQuestionaireModel

class MainGraphState(TypedDict):
    messages: Annotated[list, add_messages]
    thread_id: str
    questionnaire: BasicQuestionaireModel
    questionnaire_complete: bool
    intent: str
