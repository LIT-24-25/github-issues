from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import requests
import json

class MyModel:
    def __init__(self, token): #initiate gigachat model
        self.giga = GigaChat(credentials=token, model="GigaChat", verify_ssl_certs=False)
        self.giga_token = token
        with open("config/openrouter.txt", "r") as f:
            self.openrouter_token = f.readline().strip()

    def embed(self, text): #create embedding for text
        return self.giga.embeddings(text)

    def call_gigachat(self, user_question, some_chroma):
        context = some_chroma.find_embeddings(user_question)
        prompt = f"""Instruction for LLM: 
        Use information from provided issues, especially those with the label [State]:closed, to form a concise and precise answer to the user’s request. Write only possible solutions without summary and key points of the question itself.



        Context:
        =========================
        {context}
        =========================



        User question:
        {user_question}
        """
        payload = Chat(
            messages=[
                Messages(
                    role=MessagesRole.USER,
                    content=prompt
                )
            ],
            temperature=0,
        )
        response = self.giga.chat(payload)
        return context,response.choices[0].message.content
    

    def call_qwen(self, user_question, some_chroma):
        context = some_chroma.find_embeddings(user_question)
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openrouter_token}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "qwen/qwen-plus",
                "messages": [
                {
                    "role": "user",
                    "content": [
                    {
                        "type": "text",
                        "text": f"""Instruction for LLM: 
    Use information from provided issues, especially those with the label [State]:closed, to form a concise and precise answer to the user’s request. Write only possible solutions without summary and key points of the question itself.



    Context:
    =========================
    {context}
    =========================



    User question:
    {user_question}
    """
                    }
                    ]
                }
                ],
                
            }, indent=2)
            )

        data = response.json()
        return context, data['choices'][0]['message']['content']