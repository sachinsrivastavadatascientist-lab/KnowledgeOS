import os
import sys
import json
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic

from utils.config_loader import load_config
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException


# ==========================================================
# API KEY MANAGER
# ==========================================================

class ApiKeyManager:

    REQUIRED_KEYS = [
        "GROQ_API_KEY",
        "GOOGLE_API_KEY",
        "ANTHROPIC_API_KEY"
    ]

    def __init__(self):

        self.log = CustomLogger().get_logger(__name__)
        self.api_keys = {}

        raw = os.getenv("API_KEYS")

        if raw:
            try:
                parsed = json.loads(raw)

                if not isinstance(parsed, dict):
                    raise ValueError("API_KEYS is not a valid JSON object")

                self.api_keys = parsed
                self.log.info("Loaded API_KEYS from ECS Secret")

            except Exception as e:
                self.log.warning(
                    "Failed to parse API_KEYS",
                    error=str(e)
                )

        # Fallback (.env / Local)
        for key in self.REQUIRED_KEYS:

            if not self.api_keys.get(key):

                value = os.getenv(key)

                if value:
                    self.api_keys[key] = value
                    self.log.info(f"{key} loaded from environment")

        missing = [
            key
            for key in self.REQUIRED_KEYS
            if not self.api_keys.get(key)
        ]

        if missing:
            self.log.error(
                "Missing API Keys",
                missing_keys=missing
            )
            raise DocumentPortalException(
                "Missing API Keys",
                sys
            )

        self.log.info(
            "API Keys Loaded Successfully",
            available_keys=list(self.api_keys.keys())
        )

    def get(self, key: str):

        value = self.api_keys.get(key)

        if not value:
            raise KeyError(f"{key} not found")

        return value


# ==========================================================
# MODEL LOADER
# ==========================================================

class ModelLoader:

    def __init__(self):

        self.log = CustomLogger().get_logger(__name__)

        if os.getenv("ENV", "local").lower() != "production":
            load_dotenv()
            self.log.info("Running in LOCAL mode (.env loaded)")
        else:
            self.log.info("Running in PRODUCTION mode")

        self.api_key_mgr = ApiKeyManager()

        self.config = load_config()

        self.log.info(
            "YAML Config Loaded",
            config_keys=list(self.config.keys())
        )

    # ------------------------------------------------------

    def load_embeddings(self):

        try:

            self.log.info("Loading Embedding Model")

            model_name = self.config["embedding_model"]["model_name"]

            embedding = GoogleGenerativeAIEmbeddings(
                model=model_name,
                api_key=self.api_key_mgr.get("GOOGLE_API_KEY")
            )

            self.log.info(
                "Embedding Model Loaded",
                model=model_name
            )

            return embedding

        except Exception as e:

            self.log.error(
                "Failed to Load Embedding",
                error=str(e)
            )

            raise DocumentPortalException(
                "Embedding Loading Failed",
                sys
            )

    # ------------------------------------------------------

    def load_llm(self):

        try:

            llm_block = self.config["llm"]

            provider_key = os.getenv(
                "LLM_PROVIDER",
                "anthropic"
            ).lower()

            if provider_key not in llm_block:

                raise DocumentPortalException(
                    f"{provider_key} not found in config",
                    sys
                )

            llm_config = llm_block[provider_key]

            provider = llm_config["provider"]
            model_name = llm_config["model_name"]
            temperature = llm_config.get("temperature", 0.5)
            max_tokens = llm_config.get("max_output_tokens", 2048)

            self.log.info(
                "Loading LLM",
                provider=provider,
                model=model_name
            )

            if provider == "groq":

                return ChatGroq(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=self.api_key_mgr.get("GROQ_API_KEY")
                )

            elif provider == "google":

                return ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=self.api_key_mgr.get("GOOGLE_API_KEY")
                )

            elif provider == "openai":

                return ChatOpenAI(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=os.getenv("OPENAI_API_KEY")
                )

            elif provider == "anthropic":

                return ChatAnthropic(
                    model=model_name,
                    max_tokens=max_tokens,
                    api_key=self.api_key_mgr.get("ANTHROPIC_API_KEY")
                )

            else:

                raise ValueError(
                    f"Unsupported Provider : {provider}"
                )

        except Exception as e:

            self.log.error(
                "Failed to Load LLM",
                error=str(e)
            )

            raise DocumentPortalException(
                "LLM Loading Failed",
                sys
            )


# ==========================================================

if __name__ == "__main__":

    loader = ModelLoader()

    embedding = loader.load_embeddings()
    print(embedding)

    llm = loader.load_llm()

    result = llm.invoke("Hello")

    print(result.content)