from retrieve import RetrieveRepo
from chunks import ChunkSplitter
from model import Model
from mychroma import MyChroma
from model import Model
import requests
import json
from question_app.initialize import model, my_chroma

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

def get_operouter():
    with open("config/openrouter.txt", "r") as f:
        openrouter_token = f.readline()
        return openrouter_token


def create_model():
    with open("config/gigachat.txt", "r") as f:
        token = f.read()
    model = Model(token)
    return model

def model_call(user_question):
    retrieved_context = my_chroma.find_embeddings(user_question)
    context = ''
    for i in retrieved_context:
        context = context + i[0] + ". " + i[1]['comment'] + "\n\n"
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {get_operouter()}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "qwen/qwen-plus",
            "messages": [
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": f"""Instruction for LLM: 
Use information from provided issues, especially those with the label [State]:closed, to form a concise and precise answer to the user’s request. Write only possible solutions without summary and key points of the question itself.



Context:
=========================
{context}
=========================



User question:
{user_question}
"""
                }
                ]
            }
            ],
            
        }, indent=2)
        )

    data = response.json()
    return context, data['choices'][0]['message']['content']


def train_process():
    get_data()
    chunk_splitter = ChunkSplitter()
    output = chunk_splitter.create_chunks()
    model = create_model()
    my_chroma = MyChroma()
    my_chroma.fill_data(output, model)
