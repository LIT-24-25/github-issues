import json
from langchain_text_splitters import RecursiveCharacterTextSplitter;

class ChunkSplitter():
  def __init__(self):
    with open('data.json', "r") as json_data:
      self.data = json.load(json_data)

  def create_chunks(self):
    chunks = {}
    for question in self.data.keys():
      text = self.data[question]
      splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter( 
      chunk_size=50,
      chunk_overlap = 10
      )
      output = splitter.create_documents([text])
      chunks[question] = []
      for part in output:
        chunks[question].append(part.page_content)
    with open("chunks.json", "w") as f:
      json.dump(chunks, f, indent=4)