
import os
from openai import OpenAI
import logfire
from dotenv import load_dotenv

load_dotenv()
logfire.configure(
    token=os.environ.get('LOGFIRE_KEY'),
)

API_KEY = ""
if not API_KEY:
    API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is not set. Please set the API key as a static variable or in the environment variable OPENAI_API_KEY."
    )

llm = OpenAI(api_key=API_KEY)
logfire.instrument_openai(llm)
