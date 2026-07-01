import os
import sys
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_groq import ChatGroq
from utils.config_loader import load_config

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


# intializing logger

class ApiKeyManager:
    REQUIRED_KEYS = ["GROQ_API_KEY","ANTHROPIC_API_KEY","GOOGLE_API_KEY"]
    
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
                self.log.info("Loaded API_KEYS from ECS secret")
            except Exception as e:
                self.log.warning("Failed to parse API_KEYS as JSON", error=str(e))

        # Fallback to individual env vars
        for key in self.REQUIRED_KEYS:
            if not self.api_keys.get(key):
                env_val = os.getenv(key)
                if env_val:
                    self.api_keys[key] = env_val
                    self.log.info(f"Loaded {key} from individual env var")

        # Final check
        missing = [k for k in self.REQUIRED_KEYS if not self.api_keys.get(k)]
        if missing:
            self.log.error("Missing required API keys", missing_keys=missing)
            raise DocumentPortalException("Missing API keys", sys)

        self.log.info("API keys loaded", keys={k: v[:6] + "..." for k, v in self.api_keys.items()})


    def get(self, key: str) -> str:
        val = self.api_keys.get(key)
        if not val:
            raise KeyError(f"API key for {key} is missing")
        return val


class ModelLoader:
    """
    Loads embedding models and LLMs based on config and environment.
    """

    def __init__(self):
        if os.getenv("ENV", "local").lower() != "production":
            load_dotenv()
            self.log.info("Running in LOCAL mode: .env loaded")
        else:
            self.log.info("Running in PRODUCTION mode")

        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()
        self.log.info("YAML config loaded", config_keys=list(self.config.keys()))


    def get(self, key: str) -> str:
        val = self.api_keys.get(key)
        if not val:
            raise KeyError(f"API key for {key} is missing")
        return val
        

    def _validate_env(self):
        required_vars=["GROQ_API_KEY",
                        "OPENAI_API_KEY",
                         "GOOGLE_API_KEY",
                         "ANTHROPIC_API_KEY"]
        self.api_keys={key:os.getenv(key) for key in required_vars}
        missing = [k for k,v in self.api_keys.items() if not v]
        if missing:
            self.log.error("Missing enviorment variables",missing_vars=missing)
            raise DocumentPortalException("Missing enviorment variables",sys)
        self.log.info("Enviorment variables validated",avilabel_keys = [k for k in self.api_keys.keys() if self.api_keys[k]])

    ####################################################3
    
    
    
    
    # ##################################################    

    def load_embeddings(self):
        try:
            self.log.info("Loading embedding model....")
            model_name = self.config["embedding_model"]["model_name"]
           
            return GoogleGenerativeAIEmbeddings(model=model_name,
                                    api_key=self.api_key_mgr.get("GOOGLE_API_KEY"))
                                   
        except Exception as e:
            self.log.error("Error loading embedding model",error=str(e),model_name=self.config["embedding_model"]["model_name"])
            raise DocumentPortalException("Error loading embedding model",sys)

    def load_llm(self):
        llm_block = self.config["llm"]
        self.log.info("Loading LLM")
        
        # choose from ENV or default provider
        provider_key = os.getenv("LLM_PROVIDER","anthropic") # Default groq
        if not provider_key or provider_key.lower() not in llm_block:
            log.error("LLM provider not found in config",provider_key=provider_key)
            raise DocumentPortalException("LLM provider not found in config",sys)

        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature",0.5)
        max_tokens = llm_config.get("max_output_tokens",2048)


        log.info("loading LLM",provider=provider,model_name=model_name,temperature=temperature,max_tokens=max_tokens)
    
        if provider == "groq":
            llm = ChatGroq(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=self.api_keys["GROQ_API_KEY"]
          )
            return llm

        elif provider == "google":
            llm=ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self.api_keys["GOOGLE_API_KEY"]
            )  
            return llm 

        elif provider == "openai":
            llm=ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self.api_keys["OPENAI_API_KEY"]
            )   
            return llm

        elif provider == "anthropic":
            llm = ChatAnthropic(
                    model=model_name,
                    max_tokens=max_tokens,
                    api_key=self.api_keys["ANTHROPIC_API_KEY"]
                )

            return llm   
            


if __name__ == "__main__":
    model_loader = ModelLoader()

    embedding = model_loader.load_embeddings()
    print("loading embedding model",embedding)
    
    llm = model_loader.load_llm()
    print("loading llm",llm)

    # Test the ModelLoader
    result = llm.invoke("Hello,how are you?")
    print("Test Result\n\n\n\n\n",result.content)    