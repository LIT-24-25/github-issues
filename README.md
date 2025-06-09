# GitHelp 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

GitHelp is an intelligent technical support system for GitHub repositories that leverages the power of AI to automatically answer user questions through GitHub Issues. By integrating advanced language models and embeddings, GitHelp provides accurate, context-aware responses to repository-specific queries.

## Features ✨

- **AI-Powered Responses**: Utilizes state-of-the-art language models to generate accurate and helpful responses
- **Context-Aware**: Learns from your repository's existing issues to provide relevant answers
- **GitHub Issues Integration**: Seamlessly works with GitHub's native issue system
- **Easy to Deploy**: Simple setup process with clear configuration steps
- **Customizable**: Supports multiple AI providers (OpenRouter and GigaChat)

## Architecture 🏗️

GitHelp works by:
1. Training on your repository's existing issues to build a knowledge base
2. Monitoring new issues for questions
3. Using AI to generate appropriate responses
4. Automatically posting responses as issue comments

## Prerequisites 📋

Before you begin, ensure you have:
- Python 3.10 or higher installed
- Git installed
- Access to GitHub repository with admin privileges
- API keys for OpenRouter and GigaChat
- GitHub Personal Access Token

## Setup Guide 🛠️

1. Clone the repository
```
git clone https://github.com/LIT-24-25/github-issues.git
```
2. Create a .env file in the root directory and add the following variables:
    - OPENROUTER - Your OpenRouter API key (In order to get it, you need to register on https://openrouter.ai/)
    - GIGACHAT - Your Gigachat API key (In order to get it, you need to register on https://developers.sber.ru/ and at least buy a package for embeddings)
    - OWNER - Name of the repository owner
    - REPO - Name of the repository
    - GITHUB - Your Github token (Here is how to do it: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

3. Run a command in terminal to install all necessary packages (paste path to the file in your system)
```
pip install -r /path/to/requirements.txt
```

4. Run train_model command to train the model on your repository's issues
```
python manage.py train_model
```

5. Run the server
```
python manage.py runserver
```

6. Open the browser and go to http://127.0.0.1:8000/ or http://localhost:8000/

## Configuration Options ⚙️

The following environment variables can be configured:
- `OPENROUTER`: OpenRouter API key for main language model
- `GIGACHAT`: GigaChat API key for embeddings
- `OWNER`: GitHub repository owner username
- `REPO`: GitHub repository name
- `GITHUB`: GitHub Personal Access Token

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

If you have any questions or need help with setup, please:
1. Check existing issues for answers
2. Create a new issue if you can't find an answer
3. Provide as much detail as possible about your setup and the problem you're experiencing

You can also write to author:
Telegram @Aletavrus
## Acknowledgments 🙏

- OpenRouter for providing the language model API
- GigaChat for providing the embeddings API
- All contributors who help improve this project
