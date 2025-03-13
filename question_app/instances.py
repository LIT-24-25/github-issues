import os
import environ

class InstanceConfig:
    _initialized = False

    def __init__(self):
        from business_logic.mychroma import MyChroma
        from business_logic.mymodel import MyModel
        if not self._initialized:
            self.env = environ.Env(DEBUG=(bool, False))
            BASE_DIR = os.getcwd()
            environ.Env.read_env(os.environ.get("ENV_FILE", os.path.join(BASE_DIR, ".env")))

            # Store the tokens as instance attributes
            self.openrouter_token = self.env("OPENROUTER", default="openrouter")
            self.gigachat_token = self.env("GIGACHAT", default="gigachat")
            self.owner = self.env("OWNER", default="HumanSignal")
            self.repo = self.env("REPO", default="label-studio")
            self.github_token = self.env("GITHUB", default="github")

            self.my_model = MyModel(self.gigachat_token, self.openrouter_token)
            self.my_chroma = MyChroma(self.my_model)

            # Mark as initialized to avoid re-initialization
            InstanceConfig._initialized = True

config = InstanceConfig()

# Define variables for direct import access
openrouter_token = config.openrouter_token
gigachat_token = config.gigachat_token
my_model = config.my_model
my_chroma = config.my_chroma
owner = config.owner
repo = config.repo
github_token = config.github_token