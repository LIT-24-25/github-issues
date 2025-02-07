from gigachat import GigaChat

class Model:
    def __init__(self, token): #initiate gigachat model
        self.giga = GigaChat(credentials=token, model="GigaChat-Max", verify_ssl_certs=False)

    def embed(self, text): #create embedding for text
        return self.giga.embeddings(text)

    def invoke(self, context:str):
        response = self.giga.chat(context)
        return response.choices[0].message.content