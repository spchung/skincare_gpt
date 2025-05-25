from typing import Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from app.lang_graphs.chat_v1.graph_state import MainGraphState
from app.lang_graphs.chat_v1.memory.thread_context import get_context_store
from app.lang_graphs.chat_v1.models.basic_questioinaire import (
    BasicQuestionaireModel,
    BasicQuestionaireModel_Gender,
    BasicQuestionaireModel_SkinType,
    BasicQuestionaireModel_HasRoutine,
    BasicQuestionaireModel_RoutineDescription,
    BasicQuestionaireModel_ProductsUsed
)

FIELD_QUESTIONS = {
    "gender": "What is your gender?",
    "skin_type": "What is your skin type? (e.g., dry, oily, combination, sensitive)",
    "has_routine": "Do you have a skincare routine?",
    "routine_description": "Please describe your current skincare routine.",
    "products_used": "What skincare products have you used? Please list them one by one."
}

# helper
def is_questionnaire_complete(form: BasicQuestionaireModel) -> bool:
    if form.has_routine == False and form.gender and form.skin_type:
        return True
    
    return all(getattr(form, field) is not None for field in FIELD_QUESTIONS)

def get_next_question(form: BasicQuestionaireModel) -> Tuple[str, Optional[str]]:
    missing_fields = [field for field in FIELD_QUESTIONS if getattr(form, field) is None]
    
    if missing_fields:
        field = missing_fields[0]
        
        # update current field
        form.current_field = field
        return FIELD_QUESTIONS[field], field
    
    return "Thank you for completing the questionnaire!", None

def get_init_question(form: BasicQuestionaireModel) -> Tuple[str, str]:
    question, field = get_next_question(form)
    
    # update current field
    form.current_field = field
    
    # TODO: implement a prompt library
    init_question = "Hi, I'm a skincare assistant. Let's start with a few questions to help me understand your skin care routine.\n"
    init_question += question

    return init_question, field

## invocation function
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
# process user answer
def answer_field(current_form: BasicQuestionaireModel, field: str, user_answer: str) -> BasicQuestionaireModel:
    if field == "gender":
        struct_llm = llm.with_structured_output(BasicQuestionaireModel_Gender)
        output = struct_llm.invoke(user_answer)
        current_form.gender = output.gender
        return current_form
    elif field == "skin_type":
        struct_llm = llm.with_structured_output(BasicQuestionaireModel_SkinType)
        output = struct_llm.invoke(user_answer)
        current_form.skin_type = output.skin_type
        return current_form
    elif field == "has_routine":
        struct_llm = llm.with_structured_output(BasicQuestionaireModel_HasRoutine)
        output = struct_llm.invoke(user_answer)
        current_form.has_routine = output.has_routine
        return current_form
    elif field == "routine_description":
        struct_llm = llm.with_structured_output(BasicQuestionaireModel_RoutineDescription)
        output = struct_llm.invoke(user_answer)
        current_form.routine_description = output.routine_description
        return current_form
    elif field == "products_used":
        struct_llm = llm.with_structured_output(BasicQuestionaireModel_ProductsUsed)
        output = struct_llm.invoke(user_answer)
        current_form.products_used = output.products_used
        return current_form
    else:
        return current_form

## Handler Node
def questionnaire_handler(state: MainGraphState):
    thread_context_store = get_context_store()

    """Process the questionnaire state and determine next action"""
    if state['questionnaire'] is None:
        raise ValueError("Questionnaire not found in state")
    
    questionnaire = state['questionnaire']
    
    # Get the last user message
    last_message = state['messages'][-1]
    if not isinstance(last_message, HumanMessage):
        raise ValueError("Last message is not a human message")
    
    if is_questionnaire_complete(questionnaire):
        ## Tell user already completed
        pass

    # Process the answer if we have a current field
    if not questionnaire.current_field:
        ## init questionnaire
        init_question, _ = get_init_question(questionnaire)
        return {
            "messages": [AIMessage(content=init_question)],
            "questionnaire": questionnaire,
        }
        
    questionnaire = answer_field(
        questionnaire, 
        questionnaire.current_field, 
        last_message.content
    )

    question, _ = get_next_question(questionnaire)
    # save thread context
    thread_context_store.set_thread_questionnaire(state['thread_id'], questionnaire)
    
    # exit 
    if is_questionnaire_complete(questionnaire):
        return {
            "messages": [AIMessage(content=" Great! Thank you for completing the questionnaire! What can I you with today?")],
            "questionnaire": questionnaire,
        }

    return {
        "messages": [AIMessage(content=question)],
        "questionnaire": questionnaire,
    }