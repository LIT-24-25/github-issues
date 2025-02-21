from gigachat import GigaChat
import requests
import json

class Model:
    def __init__(self, token): #initiate gigachat model
        self.giga = GigaChat(credentials=token, model="GigaChat", ca_bundle_file="russian_trusted_root_ca.cer")
        with open("config/openrouter.txt", "r") as f:
            self.openrouter_token = f.readline()

    def embed(self, text): #create embedding for text
        return self.giga.embeddings(text)

    def invoke(self, context:str):
        response = self.giga.chat(context)
        return response.choices[0].message.content
    

    def model_call(self, user_question, some_chroma):
        print('entered model call')
        print(f"Chroma is {some_chroma}")
        retrieved_context = some_chroma.find_embeddings(user_question)
        print('retrieved')
        context = ''
        for i in retrieved_context:
            context = context + i[0] + ". " + i[1]['comment'] + "\n\n"
        print('here')
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