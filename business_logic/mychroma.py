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
        
        # Create progress bar
        pbar = tqdm(total=len(docs), desc="Adding documents to ChromaDB", unit="doc")
        
        for idx, doc in enumerate(docs, 1):
            embedding = self.model.embed(doc.page_content)
            self.collection.add(
                documents=[doc.page_content],
                embeddings=[embedding.data[0].embedding],
                metadatas=[doc.metadata],
                ids=[f"doc_{idx}"]
            )
            pbar.update(1)
            if idx % 10 == 0:  # Log progress every 10 documents
                logger.info(f"Added {idx}/{len(docs)} documents to collection")
        
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
