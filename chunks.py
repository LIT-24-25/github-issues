import json
from langchain_text_splitters import RecursiveCharacterTextSplitter;

class ChunkSplitter():
  def __init__(self):
    with open('data.json', "r") as json_data:
      self.data = json.load(json_data)

  def create_chunks(self):
    self.output = []
    for question, content in self.data.items():
      text = [content]
      splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter( 
      chunk_size=50,
      chunk_overlap = 10
      )
      metadata = {"title": question}
      self.output.extend(splitter.create_documents(text, [metadata]))