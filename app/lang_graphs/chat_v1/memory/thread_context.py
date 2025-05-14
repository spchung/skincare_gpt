from pydantic import BaseModel
from app.lang_graphs.chat_v1.models.basic_questioinaire import BasicQuestionaireModel


class ThreadContext(BaseModel):
    thread_id: str
    questionnaire: BasicQuestionaireModel


## temp - be replaced with redis
class ThreadContextStore:
    def __init__(self):
        self.context_store = {}

    def get_thread_context(self, thread_id: str) -> ThreadContext:
        if thread_id not in self.context_store:
            self.context_store[thread_id] = ThreadContext(thread_id=thread_id, questionnaire=BasicQuestionaireModel())
        return self.context_store[thread_id]

    def set_thread_context(self, thread_id: str, context: ThreadContext):
        if thread_id not in self.context_store:
            self.context_store[thread_id] = context
        self.context_store[thread_id] = context

    def set_thread_questionnaire(self, thread_id: str, questionnaire: BasicQuestionaireModel):
        if thread_id not in self.context_store:
            self.context_store[thread_id] = ThreadContext(thread_id=thread_id, questionnaire=BasicQuestionaireModel())
        self.context_store[thread_id].questionnaire = questionnaire

    def info(self):
        print(f"ThreadContextStore: {len(self.context_store)} threads")
        for thread_id, context in self.context_store.items():
            print(f"  - {thread_id}: {context.questionnaire.model_dump_json()}")

context_store = None

def get_context_store():
    global context_store
    if context_store is None:
        context = ThreadContextStore()
    return context
