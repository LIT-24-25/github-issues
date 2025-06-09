from setuptools import setup, find_packages

setup(
    name="github-issues",
    version="0.1.0",
    author="Alex Glybov",
    author_email="alex.glybov@gmail.com",
    description="A package for making a website for tech support of Github Repositories with Github Issues",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LIT-24-25/github-issues",
    packages=find_packages(),
    install_requires=[
        "pytest==8.3.4",
        "vcrpy==7.0.0",
        "requests==2.32.3",
        "langchain-core==0.3.41",
        "langchain-text-splitters==0.3.6",
        "python-dotenv==1.0.1",
        "setuptools==75.1.0",
        "Django==5.1.6",
        "djangorestframework==3.15.2",
        "gigachat==0.1.38",
        "django-environ==0.12.0",
        "openai==1.69.0",
        "chromadb==0.6.3",
        "tqdm==4.67.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # Minimum Python version required
)