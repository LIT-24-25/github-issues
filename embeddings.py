from gigachat import GigaChat
from langchain_core.documents import Document
from langchain_gigachat.embeddings import GigaChatEmbeddings

class Embeddings:
    def __init__(self, token):
        self.giga = GigaChat(credentials=token, verify_ssl_certs=False)
        self.gigachat_embeddings = GigaChatEmbeddings(credentials="ключ_авторизации")


    def embed(self, text):
        return self.giga.embeddings(text)