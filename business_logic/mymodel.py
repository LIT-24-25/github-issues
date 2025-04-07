from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import requests
import json

class MyModel:
    def __init__(self, gigachat_token, openrouter_token): #initiate gigachat model
        self.gigachat_token = gigachat_token
        self.openrouter_token = openrouter_token
        self.giga = GigaChat(credentials=self.gigachat_token, model="GigaChat", verify_ssl_certs=False)

    def embed(self, text): #create embedding for text
        return self.giga.embeddings(text)

    def call_gigachat(self, user_question, some_chroma):
        context, urls = some_chroma.find_embeddings(user_question)
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
        print(urls)
        return urls, response.choices[0].message.content
    

    def call_openrouter(self, user_question, some_chroma):
        context, urls = some_chroma.find_embeddings(user_question)
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openrouter_token}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "models": ["deepseek/deepseek-chat-v3-0324:free", "meta-llama/llama-4-maverick:free", "deepseek/deepseek-v3-base:free"],
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
        print(data)
        # Add error handling for the response
        if 'error' in data:
            return urls, f"Error: {data['error']['message']}", "OpenRouter"
        
        # Check if the expected structure exists
        if 'choices' in data and len(data['choices']) > 0 and 'message' in data['choices'][0]:
            return urls, data['choices'][0]['message']['content'], data["model"]
        else:
            # Return a fallback or log the unexpected structure
            return urls, "Unexpected response structure: " + str(data), "OpenRouter"