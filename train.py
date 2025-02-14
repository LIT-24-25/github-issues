from retrieve import RetrieveRepo
from chunks import ChunkSplitter
from model import Model
from mychroma import MyChroma
from retrieve import RetrieveRepo
from chunks import ChunkSplitter
from model import Model
from langchain_core.messages import HumanMessage, SystemMessage

def get_data():
    owner, repo, token = read_config()
    fetch = RetrieveRepo(owner, repo, token)
    fetch.get_issues()
    fetch.get_issues_comments()

def read_config():
    with open("config/config.txt.", "r") as f:
        lines = f.readlines()
        owner = lines[0].replace("\n", "")
        repo = lines[1].replace("\n", "")
        token = lines[2].replace("\n", "")
    return owner, repo, token

def create_model():
    with open("config/gigachat.txt", "r") as f:
        token = f.read()
    model = Model(token)
    return model

def model_call(user_question):
    model = create_model()
    my_chroma = MyChroma(model)
    retrieved_context = my_chroma.find_embeddings(user_question)
    context = ''
    for i in retrieved_context:
        context = context + i[0] + ". " + i[1]['comment'] + "\n\n"
    messages = [
    HumanMessage(
    content=f"""Instruction for LLM: 
Use information from provided issues, especially those with the label [State]:closed, to form a concise and precise answer to the user’s request. Write only possible solutions without summary and key points of the question itself.



Context:
=========================
{context}
=========================



User question:
{user_question}
"""
)
]
    response = model.invoke(context)
    return response


def train_process():
    # get_data()
    # chunk_splitter = ChunkSplitter()
    # output = chunk_splitter.create_chunks()
    model = create_model()
    my_chroma = MyChroma(model)
