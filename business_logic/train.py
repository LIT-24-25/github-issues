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
    from business_logic.retrieve import RetrieveRepo
    from question_app.instances import gigachat_token, openrouter_token, owner, repo, github_token
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Get data and capture fetch instance plus repo info
    fetch, owner, repo = get_data()
    
    chunk_splitter = ChunkSplitter()
    output = chunk_splitter.create_chunks()
    
    # Check if chunks were created successfully
    if not output or len(output) == 0:
        logger.error("No chunks were created. Check your data and chunking process.")
        return
    
    logger.info(f"Successfully created {len(output)} chunks for embedding")
    
    # Output a sample of the first chunk to verify content
    if output:
        logger.info(f"Sample chunk: {output[0].page_content[:100]}...")
        logger.info(f"Sample metadata: {output[0].metadata}")
    
    my_model_train = MyModel(gigachat_token, openrouter_token)
    my_chroma_train = MyChroma(my_model_train)
    
    # Fill ChromaDB with chunks
    logger.info("Starting to fill ChromaDB with chunks...")
    my_chroma_train.fill_data(output)
    logger.info("Finished filling ChromaDB")
    
    # Verify data was added by querying a sample
    try:
        logger.info("Verifying data was added correctly...")
        # Use a generic query to check if data exists
        context, urls = my_chroma_train.find_embeddings("test query")
        if context:
            logger.info("Data verification successful - retrieved context from ChromaDB")
        else:
            logger.warning("Data verification warning - no context retrieved from ChromaDB")
    except Exception as e:
        logger.error(f"Error verifying data: {str(e)}")
    
    # Save training metadata at the end of the process
    fetch = RetrieveRepo(owner, repo, github_token)
    metadata_file = save_training_metadata(owner, repo, fetch)
    print(f"Training metadata saved to: {metadata_file}")