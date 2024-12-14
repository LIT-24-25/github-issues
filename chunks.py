import json
from langchain_text_splitters import RecursiveCharacterTextSplitter;

with open('data.json', "r") as json_data:
  d = json.load(json_data)


chunks = {}
for question in d.keys():
  text = d[question]
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