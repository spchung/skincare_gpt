from pydantic import BaseModel, Field
from typing import Literal

class ProductSearchFilter(BaseModel):
    data_type: Literal["int", "float", "str"] = Field(..., description="The type of filter to extract from the user's query.")
    key: str = Field(..., description="The type of filter to extract from the user's query.")
    value: int | float | str = Field(..., description="The value of the filter to extract from the user's query.")
    condition: Literal["above", "below"] = Field(..., description="The condition of the filter.")
