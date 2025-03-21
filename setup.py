from setuptools import setup, find_packages

setup(
    name="github-issues",
    version="0.1.0",
    author="Alex Glybov",
    author_email="alex.glybov@gmail.com",
    description="A package for making a website for tech support of Github Projects with Github Issues",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LIT-24-25/github-issues",
    install_requires=[
        "chromadb==0.6.3",
        "Django==5.1.6",
        "djangorestframework==3.15.2",
        "gigachat==0.1.38",
        "langchain-core==0.3.41",
        "langchain-text-splitters==0.3.6",
        "pytest==8.3.4",
        "python-dotenv==1.0.1",
        "requests==2.32.3",
        "setuptools==75.1.0",
        "tqdm==4.67.1",
        "vcrpy==7.0.0",
        "django-environ==0.12.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # Minimum Python version required
)