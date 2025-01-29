from retrieve import RetrieveRepo
from chunks import ChunkSplitter
from model import Model
from chroma import Chroma
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


if __name__ == '__main__':
    # get_data()
    chunkSplitter = ChunkSplitter()
    output = chunkSplitter.create_chunks()
    model = create_model()
    chroma = Chroma(output, model)
    chroma.get_data()
    userQuestion = input("Which question do you have?")
    results = chroma.find_embeddings(userQuestion)
    messages = [
    SystemMessage(
        content="Ты бот для решения проблем по программированию. Твоя задача решать проблему пользователю с помощью контекста, который тебе будет дан. При прочтении контекста отдавай большее предпочтение тем текстам, которые имеют [State]:closed."
    )
    ]
    context = userQuestion + "\n"
    for i in results:
        context = context + i[0] + ". " + i[1]['comment'] + "\n"
    messages.append(HumanMessage(content=context))
    response = model.invoke(context)
    print(response)
