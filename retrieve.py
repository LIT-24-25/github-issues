import requests
import pandas as pd
import json

base_url = "https://api.github.com"

def getIssues(owner, repo, headers):   
    url = f"{base_url}/repos/{owner}/{repo}/issues"
    response = requests.get(url, headers=headers)

    issues = []
    page = 1
    per_page = 10

    while True:
        params = {'per_page': per_page, 'page': page}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break

        page_issues = response.json()

        if not page_issues:
            break

        issues.extend(page_issues)
        page += 1

    return issues
    
def getIssuesComments(keys, headers):
    result = []
    for item in keys.values():
        url = item[0]
        print(url)
        response = requests.get(url, headers=headers)
    
        if response.status_code == 200:
            repositories_data = response.json()
            if len(repositories_data)!=0:
                result.append(repositories_data[0]["body"])
            else:
                result.append("No description provided")
        else:
            print(f"Failed to retrieve comments. Status code: {response.status_code}")
            return None
    return result
    

username = "USERNAME"
repo = "REPO_NAME"
personal_access_token = "TOKEN"

headers = {
    'Authorization': f"Bearer {personal_access_token}"}

data = {}

issues = getIssues(username, repo, headers)
if issues:
    for issue in issues:
        data[(issue["title"] + " " + "[" + issue["state"] + "]")] = [issue["comments_url"], issue["body"]]
else:
    print("There are no found issues in your repo")
print(data)
comments = getIssuesComments(data, headers)
titles = list(data.keys())
if comments:
    for index in range(len(data)):
        data[titles[index]] = data[titles[index]][1] + ". " + comments[index]
else:
    print("There are no found comments in your issues")

if issues:
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)