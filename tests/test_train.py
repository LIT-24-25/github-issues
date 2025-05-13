from business_logic.retrieve import RetrieveRepo
from business_logic.chunks import ChunkSplitter
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pytest
import vcr
import os
from io import StringIO
from dotenv import load_dotenv
from unittest.mock import MagicMock
from tests.mocked_issues import cont_1, cont_2
import requests
from functools import wraps
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

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
        cassette_library_dir='./tests',
        record_mode=vcr.record_mode.RecordMode.ONCE,
        filter_headers=['authorization', 'Authorization', 'Bearer'],
        before_record_request=before_record_request,
        before_record_response=before_record_response,
        match_on=['uri', 'method', 'query']
    )
    return myvcr

def with_vcr(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cassette_name = f'cassettes/{func.__name__}.yaml'
        with vcr.VCR(
            cassette_library_dir='./tests',
            record_mode=vcr.record_mode.RecordMode.ONCE,
            filter_headers=['authorization', 'Authorization', 'Bearer'],
            match_on=['uri', 'method', 'query']
        ).use_cassette(cassette_name):
            return func(*args, **kwargs)
    return wrapper

@with_vcr
def mocked_get_issues(self): #retrieve issues in format: title, body and state = url of comments for this issue
    print("Starting retrieval of issues")
    url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues"
    issues = []
    page = 1
    per_page = 10
    max_issues = 10
    while len(issues) < max_issues:
        params = {'per_page': per_page, 'page': page}
        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code != 200:
            break
        page_issues = response.json()
        if not page_issues or page > 1:
            break
        issues.extend(page_issues)
        print("page ", page)
        page += 1

    if issues:
        for issue in issues:
            if issue.get("body"):
                body = self.clear_issue(issue["body"])
                self.data[issue["title"]] = [issue["comments_url"], f"State: [{issue['state']}]\n{body}", issue["id"]]
            else:
                self.data[issue["title"]] = [issue["comments_url"], f"State: [{issue['state']}]", issue["id"]]
            print(issue["id"])
        print("successfully retrieved")
    else:
        print("There are no found issues in your repo")

@with_vcr
def mocked_get_issues_comments(self):  # Get comments
    print('starting to retrieve comments')
    result = []
    for item in self.data.values():
        url = item[0]
        comment = self.fetch_comments(url)
        result.append(comment)

    self.save_data(result)

# Mocked save_data function that saves to tests/issues/ instead of issues/
def mocked_save_data(self, result: list):
    print("Starting to save data to test files")
    titles = list(self.data.keys())
    
    # Create tests/issues directory if it doesn't exist
    test_issues_dir = Path("tests/issues/")
    if test_issues_dir.exists():
        import shutil
        # Use rmtree to remove directory and its contents
        try:
            shutil.rmtree(test_issues_dir)
        except PermissionError:
            print("Warning: Could not remove tests/issues directory, will try to use existing one")
    
    # Create the directory
    test_issues_dir.mkdir(exist_ok=True)
    
    # Save files
    for index, res in enumerate(result):
        if res:
            issue_data = self.data[titles[index]]
            file_path = f"tests/issues/{issue_data[2]}.md"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {titles[index]}\n")
                f.write(issue_data[1] + res)
            print(f"Saved test issue to {file_path}")
    print('Finished saving all test issues')

@pytest.mark.usefixtures("vcr_config")
def test_get_data(vcr_config):    
    # Set up test environment
    owner = os.getenv('OWNER')
    repo = os.getenv('REPO')
    token = os.getenv('GITHUB')
    
    # Create RetrieveRepo instance and get the data
    fetch = RetrieveRepo(owner, repo, token)
    # Monkey patch both methods
    original_get_issues = fetch.get_issues
    original_get_comments = fetch.get_issues_comments
    original_save_data = fetch.save_data
    fetch.get_issues = lambda: mocked_get_issues(fetch)
    fetch.get_issues_comments = lambda: mocked_get_issues_comments(fetch)
    fetch.save_data = lambda result: mocked_save_data(fetch, result)
    
    try:
        fetch.get_issues()
        fetch.get_issues_comments()
    finally:
        # Restore original methods
        fetch.get_issues = original_get_issues
        fetch.get_issues_comments = original_get_comments
        fetch.save_data = original_save_data

    # Make sure at least one issue file exists in the directory
    test_issues_dir = "tests/issues/"
    issue_files = os.listdir(test_issues_dir)
    assert len(issue_files) > 0, "No issue files were created by the mocked functions"
    
    # Verify content of files
    for issue_file in issue_files:
        if issue_file.endswith(".md"):
            file_path = os.path.join(test_issues_dir, issue_file)
            assert os.path.exists(file_path), f"Failed to create test file {file_path}"

@pytest.fixture
def mock_file_data(monkeypatch):
    # Mock os.listdir to return a fixed list of filenames (hardcoded)
    monkeypatch.setattr(os, 'listdir', lambda _: [
        '2910730993.md',
        '2915106578.md'
    ])
    
    # Create a custom file-like object that properly handles readline() and read()
    class MockFile:
        def __init__(self, content):
            self.content = content
            self.lines = content.splitlines(True)  # Keep the newlines
            self.line_index = 0
            self.read_called = False
            
        def readline(self):
            if self.line_index < len(self.lines):
                line = self.lines[self.line_index]
                self.line_index += 1
                return line
            return ''
            
        def read(self):
            if not self.read_called:
                self.read_called = True
                # Return everything except the first line
                return ''.join(self.lines[self.line_index:])
            return ''
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    # Mock open to return the content of the file dynamically
    def custom_open(filename, *args, **kwargs):
        file_contents = {
            'tests/issues/2910730993.md': cont_1,
            'tests/issues/2915106578.md': cont_2,
        }
        # Extract the base filename without the directory prefix
        base_filename = filename.split('/')[-1]
        if filename in file_contents:
            return MockFile(file_contents[filename])
        elif f'tests/issues/{base_filename}' in file_contents:
            return MockFile(file_contents[f'tests/issues/{base_filename}'])
        return StringIO('')  # Return empty string if file is not found
    
    monkeypatch.setattr('builtins.open', custom_open)
    
    # Mock os.path.exists to return True for the test issues directory
    original_exists = os.path.exists
    def mock_exists(path):
        if path == 'tests/issues/' or path == Path('tests/issues/'):
            return True
        return original_exists(path)
    
    monkeypatch.setattr(os.path, 'exists', mock_exists)
    
    # Mock os.path.join to handle path joining correctly
    original_join = os.path.join
    def mock_join(*args):
        if args[0] == 'tests/issues/' and len(args) > 1:
            return f'tests/issues/{args[1]}'
        return original_join(*args)
    
    monkeypatch.setattr(os.path, 'join', mock_join)

@pytest.fixture
def mock_text_splitter(monkeypatch):
    # Create mock for the splitter class and instance
    mock_splitter_class = MagicMock()
    mock_splitter_instance = MagicMock()
    mock_splitter_class.return_value = mock_splitter_instance
    
    # Configure the mock instance's create_documents method
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
    
    # Replace the actual class with our mock
    monkeypatch.setattr(RecursiveCharacterTextSplitter, '__new__', lambda cls, *args, **kwargs: mock_splitter_instance)
    
    return mock_splitter_instance

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