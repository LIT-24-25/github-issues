from retrieve import RetrieveRepo
import asyncio
from chunks import ChunkSplitter
from embeddings import Embeddings

def get_data():
    with open("config.txt.", "r") as f:
        lines = f.readlines()
        username = lines[0].replace("\n", "")
        repo = lines[1].replace("\n", "")
        token = lines[2].replace("\n", "")
    fetch = RetrieveRepo(username, repo, token)
    asyncio.run(fetch.get_issues())
    asyncio.run(fetch.get_issues_comments())

def get_embeddings():
    with open("gigachat.txt", "r") as f:
        token = f.read()
    model = Embeddings(token)
    model.generate_embeddings(chunkSplitter.output)

chunkSplitter = ChunkSplitter()
chunkSplitter.create_chunks()
get_embeddings()