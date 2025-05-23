'''
This module contains the workflow for the product qa intent.

QA intent is when a specific product is mentioned and the user has a specific question for this product.
'''

from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage
from app.internal.postgres import get_db_tracking
from app.models.sephora import *

class ProductQAInputSchema(TypedDict):
    query: str
