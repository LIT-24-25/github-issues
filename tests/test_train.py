from train import read_config, RetrieveRepo
from chunks import ChunkSplitter
from model import Model
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pytest
import vcr
import os
from io import StringIO
from dotenv import load_dotenv
from unittest.mock import MagicMock
from mocked_issues import cont1, cont2

# Load environment variables from .env file
load_dotenv()

# Mock function to simulate reading from config.txt using environment variables
@pytest.fixture
def mock_read_config(monkeypatch):
    def mock_open(*args, **kwargs):
        mock_file_content = f"{os.getenv('OWNER')}\n{os.getenv('REPO')}\n{os.getenv('TOKEN')}\n"
        return StringIO(mock_file_content)

    monkeypatch.setattr('builtins.open', mock_open)

@pytest.fixture(scope='module')
def vcr_config():
    def before_record_request(request):
    # Remove or anonymize sensitive data from the request
        if 'authorization' in request.headers:
            request.headers['authorization'] = 'REDACTED'
        if 'Authorization' in request.headers:
            request.headers['Authorization'] = 'REDACTED'
        return request
    
    def before_record_response(response):
    # Remove or anonymize sensitive data from the response
        if 'authorization' in response['headers']:
            response['headers']['authorization'] = ['REDACTED']
        if 'Authorization' in response['headers']:
            response['headers']['Authorization'] = ['REDACTED']
        return response

    myvcr = vcr.VCR(
        cassette_library_dir='cassettes',
        record_mode= vcr.record_mode.RecordMode.ONCE,
        filter_headers=['authorization', 'Authorization', 'Bearer'],
        before_record_request=before_record_request,
        before_record_response=before_record_response,
    )
    return myvcr

@pytest.mark.asyncio
@pytest.mark.usefixtures("vcr_config")
async def test_get_data(mock_read_config, vcr_config):
    with vcr_config.use_cassette('cassettes/get_data_cassette.yaml'):
        owner, repo, token = read_config()
        fetch = RetrieveRepo(owner, repo, token)
        fetch.get_issues()
        fetch.get_issues_comments()

        issues_dir = "issues/"

        # Make sure the directory exists
        assert os.path.isdir(issues_dir)
        
        # Compare the generated files with the expected files
        # Here, we assume that the filenames are based on the issue ID (issue_id.md)
        for issue_file in os.listdir(issues_dir):
            if issue_file.endswith(".md"):
                issue_id = issue_file.replace(".md", "")
                
                # Check if the generated file exists
                issue_file_path = os.path.join(issues_dir, issue_file)
                assert os.path.exists(issue_file_path), f"Issue file {issue_file_path} does not exist"
                
                # Get the expected file content from the corresponding file on your local machine
                parent_dir = os.path.join(os.getcwd(), os.pardir)
                local_file_path = os.path.join(parent_dir, "issues", f"{issue_id}.md")
                
                # Compare the content of the generated file with the local file
                with open(issue_file_path, 'r', encoding='utf-8') as generated_file:
                    generated_content = generated_file.read().strip()

                with open(local_file_path, 'r', encoding='utf-8') as local_file:
                    local_content = local_file.read().strip()

                # Compare the content of the two files
                assert generated_content == local_content, f"Content of {issue_file_path} does not match local file"

class MockChroma:
    def __init__(self, docs: list[Document], model: Model):
        self.collection = MagicMock()
        self.collection.add = MagicMock()
        print("Mocked Chroma initialized.")

    def get_data(self):
        return self.collection  # Returning a mock collection

@pytest.fixture
def mock_file_data(monkeypatch):
    # Mock os.listdir to return a fixed list of filenames (hardcoded)
    monkeypatch.setattr(os, 'listdir', lambda _: [
        'issues/2793904575.md',
        'issues/2794019646.md'
    ])
    
    # Mock open to return the content of the file dynamically
    def custom_open(filename, *args, **kwargs):
        file_contents = {
            'issues/2793904575.md': cont1,
            'issues/2794019646.md': cont2,
        }
        return StringIO(file_contents.get(filename, ''))  # Return empty string if file is not found
    
    monkeypatch.setattr('builtins.open', custom_open)

@pytest.fixture
def mock_text_splitter(monkeypatch):
    # Mock RecursiveCharacterTextSplitter and its create_documents method
    mock_splitter = MagicMock()
    mock_splitter_instance = mock_splitter.return_value
    mock_splitter_instance.create_documents.side_effect = [
        [
            Document(page_content="# docs: DOC-274: Refresh", metadata={'comment': 'State: [open]\nNew template image files### . . . |  Name | Link |. |:-:|------------------------|. |<span aria-hidden="true">🔨</span> Latest commit | e8f38db1d90b310002ef0abd465ad21b7dff198c |. |<span aria-hidden="true">🔍</span> Latest deploy log | https://app.netlify.com/sites/label-studio-docs-new-theme/deploys/678aa11a4ae8f500082235c7 |'}),
            Document(page_content="Refresh template images", metadata={'comment': 'State: [open]\nNew template image files### . . . |  Name | Link |. |:-:|------------------------|. |<span aria-hidden="true">🔨</span> Latest commit | e8f38db1d90b310002ef0abd465ad21b7dff198c |. |<span aria-hidden="true">🔍</span> Latest deploy log | https://app.netlify.com/sites/label-studio-docs-new-theme/deploys/678aa11a4ae8f500082235c7 |'})
        ],
        [
            Document(page_content="# How to plot multiple time", metadata={'comment': '''State: [open]\nHello, I want to plot 8 time series stored in same file in same row, and choose between 4 labels for classification.\n\nBut i\'m getting problem importing the csv \'Problems with parsing CSV: 
Cannot find provided separator ",". Row 1:\nURL: undefined$\' what does it mean ?No comments provided'''}),
            Document(page_content="time series in same window?", metadata={'comment': '''State: [open]\nHello, I want to plot 8 time series stored in same file in same row, and choose between 4 labels for classification.\n\nBut i\'m getting problem importing the csv \'Problems with parsing CSV: 
Cannot find provided separator ",". Row 1:\nURL: undefined$\' what does it mean ?No comments provided'''})
        ]
    ]
    monkeypatch.setattr(RecursiveCharacterTextSplitter, 'create_documents', mock_splitter_instance.create_documents)

# Test case to check the functionality
def test_create_chunks(mock_file_data, mock_text_splitter):
    # Create an instance of ChunkSplitter and call create_chunks
    splitter = ChunkSplitter()
    result = splitter.create_chunks()
        # Debugging: print the result to see what is being returned
    print(f"Result length: {len(result)}")
    for doc in result:
        print(f"Document content: {doc.page_content}")
        print(f"Document metadata: {doc.metadata}")

    # Assertions to check the correctness of the mocked behavior
    assert len(result) == 4
    assert result[0].page_content == "# docs: DOC-274: Refresh"
    assert result[0].metadata["comment"] == 'State: [open]\nNew template image files### . . . |  Name | Link |. |:-:|------------------------|. |<span aria-hidden="true">🔨</span> Latest commit | e8f38db1d90b310002ef0abd465ad21b7dff198c |. |<span aria-hidden="true">🔍</span> Latest deploy log | https://app.netlify.com/sites/label-studio-docs-new-theme/deploys/678aa11a4ae8f500082235c7 |'
    assert result[1].page_content == "Refresh template images"
    assert result[2].page_content == "# How to plot multiple time"
    assert result[2].metadata["comment"] == '''State: [open]\nHello, I want to plot 8 time series stored in same file in same row, and choose between 4 labels for classification.\n\nBut i\'m getting problem importing the csv \'Problems with parsing CSV: 
Cannot find provided separator ",". Row 1:\nURL: undefined$\' what does it mean ?No comments provided'''
    assert result[3].page_content == "time series in same window?"

# Additional test case for Chroma class
#NOT POSSIBLE
# def test_chroma(mock_file_data, mock_text_splitter):
#     mock_docs = [
#         Document(page_content="# docs: DOC-274: Refresh", metadata={'comment': 'State: [open]\nNew template image files### . . . |  Name | Link |. |:-:|------------------------|. |<span aria-hidden="true">🔨</span> Latest commit | e8f38db1d90b310002ef0abd465ad21b7dff198c |. |<span aria-hidden="true">🔍</span> Latest deploy log | https://app.netlify.com/sites/label-studio-docs-new-theme/deploys/678aa11a4ae8f500082235c7 |'}),
#         Document(page_content="Refresh template images", metadata={'comment': 'State: [open]\nNew template image files### . . . |  Name | Link |. |:-:|------------------------|. |<span aria-hidden="true">🔨</span> Latest commit | e8f38db1d90b310002ef0abd465ad21b7dff198c |. |<span aria-hidden="true">🔍</span> Latest deploy log | https://app.netlify.com/sites/label-studio-docs-new-theme/deploys/678aa11a4ae8f500082235c7 |'}),
#         Document(page_content="# How to plot multiple time", metadata={'comment': '''State: [open]\nHello, I want to plot 8 time series stored in same file in same row, and choose between 4 labels for classification.\n\nBut i\'m getting problem importing the csv \'Problems with parsing CSV: 
# Cannot find provided separator ",". Row 1:\nURL: undefined$\' what does it mean ?No comments provided'''}),
#         Document(page_content="time series in same window?", metadata={'comment': '''State: [open]\nHello, I want to plot 8 time series stored in same file in same row, and choose between 4 labels for classification.\n\nBut i\'m getting problem importing the csv \'Problems with parsing CSV: 
# Cannot find provided separator ",". Row 1:\nURL: undefined$\' what does it mean ?No comments provided'''})
#     ]
#     mock_model = MagicMock()
#     mock_model.embed = MagicMock(return_value=MagicMock(data=[MagicMock(embedding=[0.1, 0.2, 0.3])]))
    
#     mock_chroma = MockChroma(mock_docs, mock_model)
#     mock_chroma.get_data()
#     assert mock_chroma.collection.add.called