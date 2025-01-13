from train import read_config, RetrieveRepo
from chunks import ChunkSplitter
import pytest
import vcr
import os
from io import StringIO
from dotenv import load_dotenv
import asyncio
from unittest.mock import patch, MagicMock, mock_open

# Load environment variables from .env file
load_dotenv()

# Mock function to simulate reading from config.txt using environment variables
@pytest.fixture
def mock_read_config(monkeypatch):
    def mock_open(*args, **kwargs):
        mock_file_content = f"{os.getenv('USERNAME')}\n{os.getenv('REPO')}\n{os.getenv('TOKEN')}\n"
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
        cassette_library_dir='tests/cassettes',
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
        username, repo, token = read_config()
        fetch = RetrieveRepo(username, repo, token)
        await fetch.get_issues()
        await fetch.get_issues_comments()

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

# @pytest.fixture
# def mock_persistent_client():
#     with patch('chromadb.PersistentClient') as MockPersistentClient:
#         # Set up the mock client
#         mock_client = MockPersistentClient.return_value
        
#         # Mock the create_collection method
#         mock_collection = MagicMock()
#         mock_client.create_collection.return_value = mock_collection
        
#         yield mock_client, mock_collection

# def test_create_collection(mock_persistent_client):
#     mock_client, mock_collection = mock_persistent_client
    
#     # Example of using the mocked client
#     client = mock_client
#     collection = client.create_collection(name="embeddings_collection")
    
#     # Assertions to verify behavior
#     mock_client.create_collection.assert_called_once_with(name="embeddings_collection")
#     assert collection == mock_collection