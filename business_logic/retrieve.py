import requests
from pathlib import Path
import re
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class RetrieveRepo:
    def __init__(self, owner, repo, token): #set properties or repo
        self.owner = owner
        self.repo = repo
        self.token = token
        self.data = {}
        self.headers = {
        'Authorization': f"Bearer {self.token}"
        }
        logger.info(f"Initialized RetrieveRepo for {owner}/{repo}")
    
    def clear_issue(self, line: str):
        trash_1 = """### <span aria-hidden="true">✅</span> Deploy Preview for *label-studio-docs-new-theme* ready!"""
        trash_2 = "\r\n"
        trash = [trash_1, trash_2]
        for i in trash:
            line = line.replace(i.strip(), "")
        return line
    
    def clear_comment(self, line: str):
        trash_1 = """<!-- [label-studio-docs-new-theme Preview](https://deploy-preview-6810--label-studio-docs-new-theme.netlify.app) -->
_To edit notification comments on pull requests, go to your [Netlify site configuration](https://app.netlify.com/sites/label-studio-docs-new-theme/configuration/notifications#deploy-webhooks)._"""
        trash_2 = """/<span aria-hidden="true">.*</span>/"""
        trash_3 = """/|<span aria-hidden="true">📱</span> Preview on mobile.*</details> |/"""
        trash_4 = """<span aria-hidden="true">✅</span> Deploy Preview for *label-studio-docs-new-theme* canceled."""
        trash_5 = """<span aria-hidden="true">✅</span> Deploy Preview for *heartex-docs* canceled."""
        trash_6 = r"\|.*?\|\n\|:-:.*?\|\n.*?\|\n"
        trash = [trash_1, trash_2, trash_3, trash_4, trash_5]
        for i in trash:
            line = line.replace(i, "")
            line = line.replace('\n', '. ')
            line = line.replace('\r', '. ')
        line = re.sub(trash_6, '', line)
        return line

    def get_issues(self): #retrieve issues in format: title, body and state = url of comments for this issue
        logger.info("Starting retrieval of issues")
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues"
        issues = []
        page = 1
        per_page = 100
        
        # Create progress bar for pages
        pbar = tqdm(desc="Retrieving issues", unit="page")
        
        while True:
            params = {'per_page': per_page, 'page': page}
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"Failed to retrieve issues. Status code: {response.status_code}")
                break
            page_issues = response.json()
            if not page_issues:
                break
            issues.extend(page_issues)
            logger.info(f"Retrieved page {page} with {len(page_issues)} issues")
            pbar.update(1)
            page += 1
        
        pbar.close()

        if issues:
            logger.info(f"Processing {len(issues)} issues")
            # Add progress bar for processing issues
            for issue in tqdm(issues, desc="Processing issues", unit="issue"):
                if issue.get("body"):
                    body = self.clear_issue(issue["body"])
                    # Store html_url (issue URL) along with other data
                    self.data[issue["title"]] = [issue["comments_url"], f"State: [{issue['state']}]\n{body}", issue["id"], issue["html_url"]]
                else:
                    # Store html_url (issue URL) along with other data
                    self.data[issue["title"]] = [issue["comments_url"], f"State: [{issue['state']}]", issue["id"], issue["html_url"]]
            logger.info("Successfully processed all issues")
        else:
            logger.warning("No issues found in the repository")

    def get_issues_comments(self):  # Get comments
        result = []
        logger.info('Starting to retrieve comments')
        total_items = len(self.data)
        
        # Add progress bar for comment retrieval
        for idx, item in enumerate(tqdm(self.data.values(), desc="Retrieving comments", unit="comment", total=total_items), 1):
            url = item[0]
            comment = self.fetch_comments(url)
            result.append(comment)

        self.save_data(result)

    def fetch_comments(self, url):  # Get single comment from API
        try:
            response = requests.get(url, headers=self.headers)
        except:
            response = ''
        
        if response=='':
            return "Failed to fetch"
            
        if response.status_code == 200:
            repositories_data = response.json()
            if repositories_data:
                logger.debug(f"Successfully retrieved comments from {url}")
                return self.clear_comment(repositories_data[0]["body"])
            else:
                logger.info(f"No comments found for {url}")
                return "No comments provided"
        else:
            logger.error(f"Failed to retrieve comments. Status code: {response.status_code}")
            return "Failed to fetch"
    
    def save_data(self, result: list): #save data
        logger.info("Starting to save data to files")
        titles = list(self.data.keys())
        
        # Create issues directory if it doesn't exist, or clear it if it does
        issues_dir = Path("issues/")
        if issues_dir.exists():
            import shutil
            # Use rmtree to remove directory and its contents
            try:
                shutil.rmtree(issues_dir)
            except PermissionError:
                logger.warning("Could not remove issues directory, will try to use existing one")
        
        # Create the directory
        issues_dir.mkdir(exist_ok=True)
        
        # Add progress bar for saving files
        for index, res in enumerate(tqdm(result, desc="Saving issues", unit="file")):
            if res:
                issue_data = self.data[titles[index]]
                file_path = f"issues/{issue_data[2]}.md"
                issue_url = issue_data[3]  # Get the issue URL saved from the API
                
                with open(file_path, "w", encoding="utf-8") as f:
                    # Write issue URL as the first line
                    f.write(f"{issue_url}\n")
                    # Then write the title and content
                    f.write(f"# {titles[index]}\n")
                    f.write(issue_data[1] + res)
                logger.debug(f"Saved issue to {file_path}")
        logger.info('Finished saving all issues')
