from business_logic.retrieve import RetrieveRepo
from business_logic.chunks import ChunkSplitter
from business_logic.mymodel import MyModel
from business_logic.mychroma import MyChroma

def get_data():
    owner, repo, token = read_config()
    fetch = RetrieveRepo(owner, repo, token)
    fetch.get_issues()
    fetch.get_issues_comments()

def read_config():
    with open("config/config.txt.", "r") as f:
        lines = f.readlines()
        owner = lines[0].strip()
        repo = lines[1].strip()
        token = lines[2].strip()
    return owner, repo, token


def create_model():
    with open("config/gigachat.txt", "r") as f:
        token = f.readline().strip()
    model = MyModel(token)
    return model


def train_process():
    get_data()
    chunk_splitter = ChunkSplitter()
    output = chunk_splitter.create_chunks()
    my_chroma_train = MyChroma(create_model())
    my_chroma_train.fill_data(output)
