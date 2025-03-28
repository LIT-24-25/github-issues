import chromadb
from langchain_core.documents import Document
from business_logic.mymodel import MyModel
import logging
from tqdm import tqdm

# Get logger instance
logger = logging.getLogger(__name__)

class MyChroma:
    def __init__(self, model: MyModel): #initiate chroma collection
        self.model = model
        logger.info("Initializing ChromaDB client")
        self.client = chromadb.PersistentClient(path="./chromadb")
        self.collection = self.client.get_or_create_collection(name="embeddings_collection")
        logger.info("Created new embeddings collection")

    def fill_data(self, docs: list[Document]): #fill data with issues and comments
        logger.info(f"Starting to add {len(docs)} documents to ChromaDB")
        
        # Prepare batch arrays
        documents = []
        metadatas = []
        ids = []
        
        # Prepare document data without progress bar
        for idx, doc in enumerate(docs, 1):
            documents.append(doc.page_content)
            metadatas.append(doc.metadata)
            ids.append(f"doc_{idx}")
        
        # Process in smaller batches to avoid connection issues
        batch_size = 100  # Adjust based on your document size
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        logger.info(f"Processing documents in {total_batches} batches of {batch_size}")
        
        # Create progress bar for the entire embedding and adding process
        pbar = tqdm(total=len(documents), desc="Processing documents", unit="doc")
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            # Create embeddings for current batch
            logger.info(f"Creating embeddings for batch {i//batch_size + 1}/{total_batches}")
            batch_embeddings = self.model.embed(batch_docs)
            batch_embed_vectors = [embedding.embedding for embedding in batch_embeddings.data]
            
            # Add current batch to the collection
            logger.info(f"Adding batch {i//batch_size + 1}/{total_batches} to collection")
            try:
                self.collection.add(
                    documents=batch_docs,
                    embeddings=batch_embed_vectors,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                logger.info(f"Successfully added batch {i//batch_size + 1}/{total_batches}")
            except Exception as e:
                logger.error(f"Error adding batch {i//batch_size + 1}/{total_batches}: {str(e)}")
                # Optionally implement retry logic here
            
            # Update progress bar after processing this batch
            pbar.update(len(batch_docs))
        
        pbar.close()
        logger.info("Successfully added all documents to collection")

    def find_embeddings(self, question):
        logger.info(f"Searching for embeddings related to: {question[:50]}...")
        user_embedding = self.model.embed(question).data[0].embedding
        logger.info(f"Did the embedding with result: {user_embedding[0]}")
        result = self.collection.query(query_embeddings=[user_embedding], n_results=10)
        documents = result.get('documents')[0]
        comments = result.get('metadatas')[0]
        logger.info(f"Found {len(documents)} relevant documents")
        
        # Add progress bar for context building
        retrieved_context = []
        for i in tqdm(range(len(documents)), desc="Building context", unit="doc"):
            retrieved_context.append([documents[i], comments[i]])
        
        context = ''
        for i in retrieved_context:
            context = context + i[0] + ". " + i[1]['comment'] + "\n\n"
        return context
