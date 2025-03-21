def get_data():
    from question_app.instances import owner, repo, github_token
    from business_logic.retrieve import RetrieveRepo
    fetch = RetrieveRepo(owner, repo, github_token)
    fetch.get_issues()
    fetch.get_issues_comments()


def train_process():
    from business_logic.chunks import ChunkSplitter
    from business_logic.mychroma import MyChroma
    from business_logic.mymodel import MyModel
    from question_app.instances import gigachat_token, openrouter_token
    get_data()
    chunk_splitter = ChunkSplitter()
    output = chunk_splitter.create_chunks()
    my_model_train = MyModel(gigachat_token, openrouter_token)
    my_chroma_train = MyChroma(my_model_train)
    my_chroma_train.fill_data(output)