import json
import asyncio
import aiohttp

BASE_URL = "https://api.github.com"

class RetrieveRepo:
    def __init__(self, username, repo, token): #set properties or repo
        self.username = username
        self.repo = repo
        self.token = token
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
        trash = [trash_1, trash_2, trash_3, trash_4, trash_5]
        for i in trash:
            line = line.replace(i, "")
        return line

    async def get_issues(self): #retrieve issues in format: title, body and state = url of comments for this issue
        url = f"{BASE_URL}/repos/{self.username}/{self.repo}/issues"
        issues = []
        page = 1
        per_page = 10
        async with aiohttp.ClientSession() as session:  # Single session for all requests
            while True:
                params = {'per_page': per_page, 'page': page}
                page_issues = self.fetch_page(session, url, params)
                if not page_issues or page==2: #for testing reasons only
                    break
                issues.append(page_issues)
                page += 1

            results = await asyncio.gather(*issues)

            issues = [issue for page_issues in results for issue in page_issues]

        self.data = {}
        if issues:
            for issue in issues:
                if issue["body"]:
                    body = self.clear_issue(issue["body"])
                    self.data[issue["title"]] = [issue["comments_url"], ("State:[" + issue["state"] + "]\n" + body)]
                else:
                    self.data[issue["title"]] = [issue["comments_url"], (" [" + issue["state"] + "]")]
        else:
            print("There are no found issues in your repo")

    async def fetch_page(self, session: aiohttp.ClientSession, url, params): #get data from a single page
        async with session.get(url, headers=self.headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error: {response.status}, {await response.text()}")
                return []

    async def get_issues_comments(self): #get comments
        result = []
        tasks = []
        async with aiohttp.ClientSession() as session:
            for item in self.data.values():
                url = item[0]
                tasks.append(self.fetch_comments(url))
        
        result = await asyncio.gather(*tasks)
        self.save_data(result)

    async def fetch_comments(self, url): #get single comment from API
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    repositories_data = await response.json()
                    if repositories_data:
                        return self.clear_comment(repositories_data[0]["body"])
                    else:
                        return "No comments provided"
                else:
                    print(f"Failed to retrieve comments. Status code: {response.status}")
                    return "Failed to fetch"
        return repositories_data
    
    def save_data(self, result: list): #save data
        titles = list(self.data.keys())
        for index, res in enumerate(result):
            if res:
                self.data[titles[index]] = self.data[titles[index]][1] + res
                with open(f"issues/{index}.md", "w", encoding="utf-8") as f:
                    f.write(f"# {titles[index]} \n")
                    f.write(self.data[titles[index]])
