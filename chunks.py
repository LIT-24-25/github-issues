import json
from langchain_text_splitters import RecursiveCharacterTextSplitter;

class ChunkSplitter():
  def __init__(self): #read retrieved data
    with open('data.json', "r") as json_data:
      self.data = json.load(json_data)

  def create_chunks(self): #create chunks from the data we received. only questions are splitted
    output = []
    for question, content in self.data.items():
      text = [question]
      splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter( 
      chunk_size=30,
      chunk_overlap = 10
      )
      metadata = {"comment": content}
      output.extend(splitter.create_documents(text, [metadata]))
    return output