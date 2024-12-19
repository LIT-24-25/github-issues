import json
from langchain_text_splitters import RecursiveCharacterTextSplitter;

class ChunkSplitter():
  def __init__(self):
    with open('data.json', "r") as json_data:
      self.data = json.load(json_data)

  def create_chunks(self):
    self.output = []
    for question in self.data.keys():
      text = [question]
      splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter( 
      chunk_size=50,
      chunk_overlap = 10
      )
      self.output.extend(splitter.create_documents(text, {"title", question}))