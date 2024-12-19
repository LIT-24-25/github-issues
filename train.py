from retrieve import RetrieveRepo
import asyncio


data = {}

with open("config.txt.", "r") as f:
    lines = f.readlines()
    username = lines[0].replace("\n", "")
    repo = lines[1].replace("\n", "")
    token = lines[2].replace("\n", "")
fetch = RetrieveRepo(username, repo, token)
asyncio.run(fetch.get_issues())
asyncio.run(fetch.get_issues_comments())    