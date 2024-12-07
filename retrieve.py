import requests

base_url = "https://api.github.com"

def getIssues(owner, repo, headers):   
    url = f"{base_url}/repos/{owner}/{repo}/issues"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        repositories_data = response.json()
        return repositories_data
    else:
        print(f"Failed to retrieve issues. Status code: {response.status_code}")
        return None
    
def getIssuesComments(keys, headers):
    result = []
    for item in keys.values():
        url = item
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
personal_access_token = "YOUR TOKEN"

headers = {
    'Authorization': f"Bearer {personal_access_token}"}

data = {}

issues = getIssues(username, repo, headers)
if issues:
    for repo in issues:
        data[repo["title"]] = repo["comments_url"]
else:
    print(f"Failed to retrieve issues.")

comments = getIssuesComments(data, headers)
titles = list(data.keys())
if comments:
    for index in range(len(data)):
        data[titles[index]] = comments[index]
else:
    print(f"Failed to retrieve comments.")

with open("data.txt", "w", encoding="utf-8") as f:
    values = list(data.values())
    for i in range(len(values)):
        output = titles[i] + " : " + values[i] + "\n"
        f.write(output)