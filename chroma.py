import chromadb
from langchain_core.documents import Document
from model import Model

class Chroma:
    def __init__(self, docs: list[Document], model: Model): #initiate chroma collection
        self.model = model
        self.client = chromadb.PersistentClient(path="./chromadb")
        self.collection = self.client.get_or_create_collection(name="embeddings_collection")
        for idx, doc in enumerate(docs):
            embedding = model.embed(doc.page_content)
            self.collection.add(
                documents=[doc.page_content],
                embeddings=[embedding.data[0].embedding],
                metadatas=[doc.metadata],
                ids=[f"doc_{idx}"]
            )
        print("Documents added to collection")

    def get_data(self): #for debugging only
        coll = self.client.get_collection(name="embeddings_collection")
        return coll

    def find_embeddings(self, question):
        emb_user = self.model.embed(question)
        result = self.collection.query(query_embeddings=[emb_user.data[0].embedding], n_results=10)
        documents = result.get('documents')