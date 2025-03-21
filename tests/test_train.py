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

@pytest.mark.asyncio
@pytest.mark.usefixtures("vcr_config")
async def test_get_data(vcr_config):    
    # Set up test environment
    owner = os.getenv('OWNER')
    repo = os.getenv('REPO')
    token = os.getenv('GITHUB')
    
    # Create RetrieveRepo instance and get the data
    fetch = RetrieveRepo(owner, repo, token)
    # Monkey patch both methods
    original_get_issues = fetch.get_issues
    original_get_comments = fetch.get_issues_comments
    fetch.get_issues = lambda: mocked_get_issues(fetch)
    fetch.get_issues_comments = lambda: mocked_get_issues_comments(fetch)
    try:
        fetch.get_issues()
        fetch.get_issues_comments()
    finally:
        # Restore original methods
        fetch.get_issues = original_get_issues
        fetch.get_issues_comments = original_get_comments

    issues_dir = "issues/"
    if not os.path.isdir(issues_dir):
        os.makedirs(issues_dir)
    os.makedirs('tests/issues', exist_ok=True)

    # Compare the generated files with the expected files
    for issue_file in os.listdir(issues_dir):
        if issue_file.endswith(".md"):
            issue_id = issue_file.replace(".md", "")
            issue_file_path = os.path.join(issues_dir, issue_file)
            
            # Compare the content of the generated file with the local file
            with open(issue_file_path, 'r', encoding='utf-8') as generated_file:
                generated_content = generated_file.read().strip()

            with open(os.path.join('tests/', issue_file_path), 'r', encoding='utf-8') as local_file:
                local_content = local_file.read().strip()

            # Compare the content of the two files
            assert generated_content == local_content, f"Content of {issue_file_path} does not match local file"

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
            'issues/2793904575.md': cont_1,
            'issues/2794019646.md': cont_2,
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