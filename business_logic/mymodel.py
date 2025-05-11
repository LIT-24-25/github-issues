from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import requests
import json
from openai import OpenAI

class MyModel:
    def __init__(self, gigachat_token, openrouter_token): #initiate gigachat model
        self.gigachat_token = gigachat_token
        self.openrouter_token = openrouter_token
        self.giga = GigaChat(credentials=self.gigachat_token, model="GigaChat", verify_ssl_certs=False)
        # Initialize OpenAI client with OpenRouter base URL
        self.openai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.openrouter_token
        )

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
    

    def call_openrouter(self, user_question, some_chroma, message_history=None):
        context, urls = some_chroma.find_embeddings(user_question)
        
        # Default system instruction
        system_instruction = """Instruction for LLM: 
        Use information from provided issues, especially those with the label [State]:closed, to form a concise and precise answer to the user's request. Write only possible solutions without summary and key points of the question itself.

        Context:
        =========================
        {context}
        =========================
        """
        
        # Prepare message history for continuous dialogue
        messages = []
        
        # Add system message with context
        messages.append({
            "role": "system",
            "content": system_instruction.format(context=context)
        })
        
        # Add message history if provided
        if message_history and len(message_history) > 0:
            messages.extend(message_history)
        
        # Add the latest user question
        messages.append({
            "role": "user",
            "content": user_question
        })
        
        try:
            response = self.openai_client.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324",
                extra_body={"models": ["qwen/qwen-plus", "qwen/qwen-max"]},
                messages=messages,
                max_retries=3
            )
            
            # Get the response content
            assistant_message = response.choices[0].message.content
            model_used = response.model
            
            return urls, assistant_message, model_used
            
        except Exception as e:
            # Handle any errors from the API
            return urls, f"Error: {str(e)}", "OpenRouter"