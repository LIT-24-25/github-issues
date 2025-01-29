from gigachat import GigaChat

class Model:
    def __init__(self, token): #initiate gigachat model
        self.giga = GigaChat(credentials=token, verify_ssl_certs=False)

    def embed(self, text): #create embedding for text
        return self.giga.embeddings(text)