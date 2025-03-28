def get_data():
    from question_app.instances import owner, repo, github_token
    from business_logic.retrieve import RetrieveRepo
    fetch = RetrieveRepo(owner, repo, github_token)
    fetch.get_issues()
    fetch.get_issues_comments()
    return fetch, owner, repo


def save_training_metadata(repo_owner, repo_name, fetch_instance):
    from datetime import datetime
    from pathlib import Path
    
    # Create metadata directory if it doesn't exist
    Path("metadata/").mkdir(exist_ok=True)
    
    # Format current date and time
    training_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get issue count from the RetrieveRepo instance
    issue_count = len(fetch_instance.data)
    
    # Create metadata file - use consistent filename for the loader
    metadata_filename = "metadata/training_metadata.txt"
    
    with open(metadata_filename, "w", encoding="utf-8") as f:
        f.write(f"Repository: {repo_owner}/{repo_name}\n")
        f.write(f"Training Date: {training_date}\n")
        f.write(f"Number of Issues: {issue_count}\n")
    
    return metadata_filename


def train_process():
    from business_logic.chunks import ChunkSplitter
    from business_logic.mychroma import MyChroma
    from business_logic.mymodel import MyModel
    from question_app.instances import gigachat_token, openrouter_token
    
    # Get data and capture fetch instance plus repo info
    fetch, owner, repo = get_data()
    
    chunk_splitter = ChunkSplitter()
    output = chunk_splitter.create_chunks()
    my_model_train = MyModel(gigachat_token, openrouter_token)
    my_chroma_train = MyChroma(my_model_train)
    my_chroma_train.fill_data(output)
    
    # Save training metadata at the end of the process
    metadata_file = save_training_metadata(owner, repo, fetch)
    print(f"Training metadata saved to: {metadata_file}")