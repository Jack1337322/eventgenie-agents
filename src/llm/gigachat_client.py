import os
import base64
from typing import Optional
from langchain_community.llms import GigaChat
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import logging

logger = logging.getLogger(__name__)

class GigaChatClient:
    """
    Wrapper for GigaChat LLM using LangChain
    """
    
    def __init__(self, temperature: float = 0.5, max_tokens: int = 2000):
        client_id = os.getenv("GIGACHAT_CLIENT_ID")
        client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
        access_token = os.getenv("GIGACHAT_ACCESS_TOKEN")  # Optional: direct token
        
        # Try to use access token if provided, otherwise use credentials
        if access_token:
            logger.info("Using GigaChat access token for authentication")
            credentials = access_token
        elif client_id and client_secret:
            # GigaChat expects base64-encoded credentials in format "client_id:client_secret"
            credentials_string = f"{client_id}:{client_secret}"
            # Encode to base64 as required by GigaChat API
            credentials = base64.b64encode(credentials_string.encode('utf-8')).decode('utf-8')
            logger.info("Using GigaChat base64-encoded client_id:client_secret for authentication")
        else:
            raise ValueError(
                "Either GIGACHAT_ACCESS_TOKEN or both GIGACHAT_CLIENT_ID and GIGACHAT_CLIENT_SECRET "
                "environment variables must be set"
            )
        
        # Try different scopes if GIGACHAT_API_PERS doesn't work
        scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
        
        try:
            logger.info(f"Initializing GigaChat client with model: GigaChat, temperature: {temperature}, max_tokens: {max_tokens}")
            logger.info(f"Client ID present: {bool(client_id)}, Client Secret present: {bool(client_secret)}")
            logger.info(f"Access Token present: {bool(access_token)}")
            logger.info(f"Using scope: {scope}")
            
            self.llm = GigaChat(
                credentials=credentials,
                model="GigaChat",
                temperature=temperature,
                max_tokens=max_tokens,
                verify_ssl_certs=False,
                scope=scope
            )
            logger.info("GigaChat client initialized successfully")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to initialize GigaChat client: {e}", exc_info=True)
            
            # Check for authentication errors during initialization
            if "403" in error_msg or "Forbidden" in error_msg or "unauthorized" in error_msg.lower():
                logger.error("GigaChat initialization failed with 403. Possible issues:")
                logger.error("- Invalid credentials format")
                logger.error(f"- Wrong scope (current: {scope}, try: GIGACHAT_API_PERS or GIGACHAT_API_CORP)")
                logger.error("- Credentials don't have required permissions")
                logger.error("- Token expired (if using access token)")
                logger.error("- Check credentials at https://developers.sber.ru/portal/products/gigachat")
                raise ValueError(
                    f"GigaChat authentication failed during initialization: {error_msg}. "
                    "Please check your GIGACHAT_CLIENT_ID and GIGACHAT_CLIENT_SECRET, "
                    "or verify your GIGACHAT_ACCESS_TOKEN is valid and not expired."
                )
            raise
    
    def create_chain(self, prompt_template: str, input_variables: list) -> LLMChain:
        """Create a LangChain chain with the given prompt template"""
        prompt = PromptTemplate(
            input_variables=input_variables,
            template=prompt_template
        )
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def generate(self, prompt: str) -> str:
        """Generate text directly from a prompt"""
        try:
            response = self.llm.invoke(prompt)
            logger.info("Generated response from GigaChat")
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def agenerate(self, prompt: str) -> str:
        """Async generate text from a prompt"""
        try:
            logger.info(f"Calling GigaChat API with prompt length: {len(prompt)}")
            response = await self.llm.ainvoke(prompt)
            logger.info(f"Generated async response from GigaChat. Response type: {type(response)}, length: {len(str(response)) if response else 0}")
            return response
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating async response: {e}", exc_info=True)
            
            # Check for authentication errors
            if "403" in error_msg or "Forbidden" in error_msg or "unauthorized" in error_msg.lower():
                logger.error("GigaChat API authentication error (403). Check credentials and scope.")
                raise RuntimeError(
                    f"GigaChat API authentication failed: {error_msg}. "
                    "Please verify GIGACHAT_CLIENT_ID and GIGACHAT_CLIENT_SECRET are correct."
                )
            raise

