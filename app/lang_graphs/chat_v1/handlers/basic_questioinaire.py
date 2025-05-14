from typing import Dict, List, Optional, Tuple, Any, Annotated, Literal
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# Your existing questionnaire model
class BasicQuestionaireModel(BaseModel):
    gender: Literal["male", "female", "non-binary", "other"] | None = Field(None, description="The gender of the user")
    skin_type: Literal["dry", "oily", "combination", "sensitive"] | None = Field(None, description="The skin type of the user")
    has_routine: bool | None = Field(None, description="Whether the user has a skin care routine")
    routine_description: str | None = Field(None, description="The description of the user's skin care routine")
    products_used: List[str] | None = Field(None, description="The products that the user has used")
    current_field: str | None = Field(None, description="The current field of the questionnaire")

class BasicQuestionaireModel_Gender(BaseModel):
    gender: Literal["male", "female", "non-binary", "other"] | None = Field(None, description="The gender of the user")

class BasicQuestionaireModel_SkinType(BaseModel):
    skin_type: Literal["dry", "oily", "combination", "sensitive"] | None = Field(None, description="The skin type of the user")

class BasicQuestionaireModel_HasRoutine(BaseModel):
    has_routine: bool | None = Field(None, description="Whether the user has a skin care routine")

class BasicQuestionaireModel_RoutineDescription(BaseModel):
    routine_description: str | None = Field(None, description="The description of the user's skin care routine")

class BasicQuestionaireModel_ProductsUsed(BaseModel):
    products_used: List[str] | None = Field(None, description="The products that the user has used")


FIELD_QUESTIONS = {
    "gender": "What is your gender?",
    "skin_type": "What is your skin type? (e.g., dry, oily, combination, sensitive)",
    "has_routine": "Do you have a skincare routine?",
    "routine_description": "Please describe your current skincare routine.",
    "products_used": "What skincare products have you used? Please list them one by one."
}

# helper
def is_form_complete(form: BasicQuestionaireModel) -> bool:
    if form.has_routine == False and form.gender and form.skin_type:
        return True
    
    return all(getattr(form, field) is not None for field in FIELD_QUESTIONS)

def get_next_question(form: BasicQuestionaireModel) -> Tuple[str, Optional[str]]:
    missing_fields = [field for field in FIELD_QUESTIONS if getattr(form, field) is None]
    
    if missing_fields:
        field = missing_fields[0]
        
        form.current_field = field

        return FIELD_QUESTIONS[field], field
    
    return "Thank you for completing the questionnaire!", None

def get_init_question(form: BasicQuestionaireModel) -> Tuple[str, str]:
    question, field = get_next_question(form)
    
    init_question = "Hi, I'm a skincare assistant. Let's start with a few questions to help me understand your skin care routine.\n"
    init_question += question
    form.current_field = field

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


if __name__ == "__main__":
    
    form = BasicQuestionaireModel()

    while not is_form_complete(form):
        question, field = get_next_question(form)
        user_answer = input(question)
        form = answer_field(form, field, user_answer)

    print(form)

    

    

