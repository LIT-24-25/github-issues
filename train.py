from retrieve import RetrieveRepo
import asyncio
from chunks import ChunkSplitter
from model import Model
from chroma import Chroma
from retrieve import RetrieveRepo
import asyncio
from chunks import ChunkSplitter
from model import Model
from chroma import Chroma

def get_data():
    username, repo, token = read_config()
    fetch = RetrieveRepo(username, repo, token)
    asyncio.run(fetch.get_issues())
    asyncio.run(fetch.get_issues_comments())

def read_config():
    with open("config/config.txt.", "r") as f:
        lines = f.readlines()
        username = lines[0].replace("\n", "")
        repo = lines[1].replace("\n", "")
        token = lines[2].replace("\n", "")
    return username, repo, token

def create_model():
    with open("config/gigachat.txt", "r") as f:
        token = f.read()
    model = Model(token)
    return model


if __name__ == '__main__':
    # get_data()
    chunkSplitter = ChunkSplitter()
    output = chunkSplitter.create_chunks()
    # model = create_model()
    # chroma = Chroma(chunkSplitter.output[0:2], model)
    # chroma.get_data()