import chromadb
from langchain_core.documents import Document
from model import Model

class MyChroma:
    def __init__(self, model: Model): #initiate chroma collection
        self.model = model
        self.client = chromadb.PersistentClient(path="./chromadb")
        self.collection = self.client.get_or_create_collection(name="embeddings_collection")

    def fill_data(self, docs: list[Document]):
        for idx, doc in enumerate(docs):
            embedding = self.model.embed(doc.page_content)
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
        user_embedding = self.model.embed(question).data[0].embedding
        result = self.collection.query(query_embeddings=[user_embedding], n_results=10)
        documents = result.get('documents')[0]
        comments = result.get('metadatas')[0]
        retrieved_context = []
        for i in range(len(documents)):
            retrieved_context.append([documents[i], comments[i]])
        return retrieved_context
