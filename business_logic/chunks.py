from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from question_app.instances import owner, repo
import logging

# Get logger
logger = logging.getLogger(__name__)

class ChunkSplitter():
	def __init__(self):
		pass

	def create_chunks(self): #create chunks from the data we received. only questions are splitted
		logger.info('Started chunking process')
		output = []
		
		# Check if issues directory exists
		issues_dir = 'issues/'
		if not os.path.exists(issues_dir):
			logger.error(f"Directory '{issues_dir}' does not exist!")
			return output
		
		# Count files to process
		issue_files = os.listdir(issues_dir)
		if not issue_files:
			logger.warning(f"No files found in '{issues_dir}' directory!")
			return output
		
		logger.info(f"Found {len(issue_files)} issue files to process")
		
		for filename in issue_files:
			try:
				file_path = os.path.join(issues_dir, filename)
				logger.debug(f"Processing file: {file_path}")
				
				with open(file_path, 'r', encoding="utf-8") as f: # open in readonly mode
					head = f.readline()
					extra = f.read()
					
					if not head.strip():
						logger.warning(f"File {filename} has empty first line")
						continue
					
					splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter( 
					chunk_size=30,
					chunk_overlap = 10
					)
					
					# Create GitHub issue URL from filename (without .md extension)
					issue_number = filename.split('.')[0]
					issue_url = f"https://github.com/{owner}/{repo}/issues/{issue_number}"
					
					# Add both comment and url to metadata
					metadata = {
						"comment": extra,
						"url": issue_url
					}
					
					chunks = splitter.create_documents([head], [metadata])
					if not chunks:
						logger.warning(f"No chunks created for file {filename}")
					else:
						logger.debug(f"Created {len(chunks)} chunks for file {filename}")
					
					output.extend(chunks)
			except Exception as e:
				logger.error(f"Error processing file {filename}: {str(e)}")
		
		logger.info(f'Ended chunking. Created a total of {len(output)} chunks')
		return output