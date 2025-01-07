from gigachat import GigaChat
from langchain_gigachat.embeddings import GigaChatEmbeddings

class Model:
    def __init__(self, token): #initiate gigachat model
        self.giga = GigaChat(credentials=token, verify_ssl_certs=False)
        self.gigachat_embeddings = GigaChatEmbeddings(credentials=token)


    def embed(self, text): #create embedding for text
        return self.giga.embeddings(text)