import requests
from pathlib import Path

class RetrieveRepo:
    def __init__(self, owner, repo, token): #set properties or repo
        self.owner = owner
        self.repo = repo
        self.token = token
        self.data = {}
        self.headers = {
        'Authorization': f"Bearer {self.token}"
        }
    
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
        trash_6 = """|<span aria-hidden="true">\s(.*?)\s</span>"""
        trash = [trash_1, trash_2, trash_3, trash_4, trash_5, trash_6]
        for i in trash:
            line = line.replace(i, "")
        return line

    def get_issues(self): #retrieve issues in format: title, body and state = url of comments for this issue
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/issues"
        issues = []
        page = 1
        per_page = 10
        while True:
            params = {'per_page': per_page, 'page': page}
            response = requests.get(url, params=params)
            if response.status_code != 200:
                break
            page_issues = response.json()
            if not page_issues or page == 2:  # For testing reasons only
                break
            issues.extend(page_issues)
            page += 1

        if issues:
            for issue in issues:
                if issue.get("body"):
                    body = self.clear_issue(issue["body"])
                    self.data[issue["title"]] = [issue["comments_url"], f"State: [{issue['state']}]\n{body}", issue["id"]]
                else:
                    self.data[issue["title"]] = [issue["comments_url"], f"State: [{issue['state']}]", issue["id"]]
        else:
            print("There are no found issues in your repo")


    def get_issues_comments(self):  # Get comments
        result = []
        for item in self.data.values():
            url = item[0]
            comment = self.fetch_comments(url)
            result.append(comment)

        self.save_data(result)

    def fetch_comments(self, url):  # Get single comment from API
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            repositories_data = response.json()
            if repositories_data:
                return self.clear_comment(repositories_data[0]["body"])
            else:
                return "No comments provided"
        else:
            print(f"Failed to retrieve comments. Status code: {response.status_code}")
            return "Failed to fetch"
    
    def save_data(self, result: list): #save data
        titles = list(self.data.keys())
        Path("issues/").mkdir(exist_ok=True)
        for index, res in enumerate(result):
            if res:
                with open(f"issues/{self.data[titles[index]][2]}.md", "w", encoding="utf-8") as f:
                    f.write(f"# {titles[index]} \n")
                    f.write(self.data[titles[index]][1] + res)
