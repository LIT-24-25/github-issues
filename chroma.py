import chromadb
from chromadb.config import Settings
from langchain_core.documents import Document
from embeddings import Embeddings

class Chroma:
    def __init__(self, docs: list[Document], model: Embeddings):
        self.client = chromadb.PersistentClient(path="./chromadb")
        self.collection = self.client.create_collection(name="embeddings_collection")
        for idx, doc in enumerate(docs):
            embedding = model.embed(doc.page_content)
            self.collection.add(
                documents=[doc.page_content],
                embeddings=[embedding.data[0].embedding],
                metadatas=[doc.metadata],
                ids=[f"doc_{idx}"]
            )
        print("Documents added to collection")

    def get_data(self):
        coll = self.client.get_collection(name="embeddings_collection")
        return coll.count()