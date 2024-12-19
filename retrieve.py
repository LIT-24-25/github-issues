import json
import asyncio
import aiohttp

BASE_URL = "https://api.github.com"

class RetrieveRepo:
    def __init__(self, username, repo, token):
        self.username = username
        self.repo = repo
        self.token = token
        self.headers = {
        'Authorization': f"Bearer {self.token}"
        }

    async def get_issues(self):   
        url = f"{BASE_URL}/repos/{self.username}/{self.repo}/issues"
        issues = []
        page = 1
        per_page = 10
        async with aiohttp.ClientSession() as session:  # Single session for all requests
            while True:
                params = {'per_page': per_page, 'page': page}
                page_issues = self.fetch_page(session, url, params)
                if not page_issues or page==10:
                    break
                issues.append(page_issues)
                page += 1

            results = await asyncio.gather(*issues)

            issues = [issue for page_issues in results for issue in page_issues]

        self.data = {}
        if issues:
            for issue in issues:
                self.data[(issue["title"] + " [" + issue["state"] + "]")] = [issue["comments_url"]]
                if issue["body"]:
                    self.data[(issue["title"] + " [" + issue["state"] + "]")].append(issue["body"])
                else:
                    self.data[(issue["title"] + " [" + issue["state"] + "]")].append("No description provided")
        else:
            print("There are no found issues in your repo")

    async def fetch_page(self, session, url, params):
        async with session.get(url, headers=self.headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error: {response.status}, {await response.text()}")
                return []            

    async def fetch_comments(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    repositories_data = await response.json()
                    if repositories_data:
                        return repositories_data[0]["body"]
                    else:
                        return "No comments provided"
                else:
                    print(f"Failed to retrieve comments. Status code: {response.status}")
                    return "Failed to fetch"
        return repositories_data

    async def get_issues_comments(self):
        result = []
        tasks = []
        async with aiohttp.ClientSession() as session:
            for item in self.data.values():
                url = item[0]
                tasks.append(self.fetch_comments(url))
        
        result = await asyncio.gather(*tasks)

        titles = list(self.data.keys())
        for index, res in enumerate(result):
            if res:
                self.data[titles[index]] = self.data[titles[index]][1] + ". " + res

        with open("data.json", "w") as f:
            json.dump(self.data, f, indent=4)
        print(self.data)