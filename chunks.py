from langchain_text_splitters import RecursiveCharacterTextSplitter
import os


class ChunkSplitter():
	def __init__(self):
		pass

	def create_chunks(self): #create chunks from the data we received. only questions are splitted
		print('started chunking')
		output = []
		for filename in os.listdir('issues/'):
			with open(os.path.join('issues/', filename), 'r', encoding="utf-8") as f: # open in readonly mode
				head = f.readline()
				extra = f.read()
				splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter( 
				chunk_size=30,
				chunk_overlap = 10
				)
				metadata = {"comment": extra}
				output.extend(splitter.create_documents([head], [metadata]))
		print('ended chunking')
		return output