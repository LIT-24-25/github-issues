import os
import environ
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

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
            
            # Load training metadata
            self.training_metadata = self._load_training_metadata()

            # Mark as initialized to avoid re-initialization
            InstanceConfig._initialized = True
            
    def _load_training_metadata(self):
        metadata_file_path = os.path.join("metadata", "training_metadata.txt")
        metadata = {
            "repository": "Not available",
            "trainingDate": "Not available", 
            "issuesCount": "Not available"
        }
        
        try:
            if not os.path.exists(metadata_file_path):
                logger.warning(f"Metadata file not found at {metadata_file_path}")
                return metadata
                
            with open(metadata_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "Repository":
                        metadata["repository"] = value
                    elif key == "Training Date":
                        metadata["trainingDate"] = value
                    elif key == "Number of Issues":
                        metadata["issuesCount"] = value
                        
            logger.info(f"Successfully loaded training metadata from {metadata_file_path}")
            
        except Exception as e:
            logger.error(f"Error loading training metadata: {str(e)}")
            
        return metadata
    
    def get_training_metadata(self):
        return self.training_metadata

config = InstanceConfig()

openrouter_token = config.openrouter_token
gigachat_token = config.gigachat_token
my_model = config.my_model
my_chroma = config.my_chroma
owner = config.owner
repo = config.repo
github_token = config.github_token
training_metadata = config.training_metadata