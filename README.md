# GitHelp
Githelp is a system for technical support of Github respositories, that uses Github Issues to answer to users' questions

## Setup
1. Clone the repository
```
git clone https://github.com/LIT-24-25/github-issues.git
```
2. Open **config/** folder and write data in those files:
    - config.txt - Here you need to have information in such order:
        - Name of the repository
        - Name of the repository owner
        - Your Github token (Here is how to do it: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
    - gigachat.txt - Here you need to have information in such order:
        - Your Gigachat API key (In order to get it, you need to register on https://developers.sber.ru/ and at least buy a package for embeddings)
    - openrouter.txt - Here you need to have information in such order:
        - Your OpenRouter API key (In order to get it, you need to register on https://openrouter.ai/)

3. Run a command in terminal to install all necessary packages (paste path to the file in your system)
```
pip install -r /path/to/requirements.txt
```

4. Run train_process command to train the model on your repository's issues
```
python manage.py train_model
```

5. Run the server
```
python manage.py runserver
```

6. Open the browser and go to http://127.0.0.1:8000/ or http://localhost:8000/
