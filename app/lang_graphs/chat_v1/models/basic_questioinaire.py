from typing import List, Literal
from pydantic import BaseModel, Field

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

