from gigachat import GigaChat
from langchain_core.documents import Document

class Embeddings:
    def __init__(self, token):
        self.giga = GigaChat(credentials=token, verify_ssl_certs=False)

    def generate_embeddings(self, docs: list[Document]):
        self.embeddings = []
        self.metadatas = []
        for doc in docs:
            embedding = self.giga.embeddings(doc.page_content)
            self.embeddings.append(embedding)
            metadata = {"title": doc.metadata.get("title", "Untitled")}
            self.metadatas.append(metadata)
        