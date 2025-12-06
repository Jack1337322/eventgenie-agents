import os
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
        
        if not client_id or not client_secret:
            raise ValueError("GIGACHAT_CLIENT_ID and GIGACHAT_CLIENT_SECRET environment variables must be set")
        
        # GigaChat expects credentials in format "client_id:client_secret"
        credentials = f"{client_id}:{client_secret}"
        
        try:
            self.llm = GigaChat(
                credentials=credentials,
                model="GigaChat",
                temperature=temperature,
                max_tokens=max_tokens,
                verify_ssl_certs=False,
                scope="GIGACHAT_API_PERS"
            )
            logger.info("GigaChat client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GigaChat client: {e}")
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
            response = await self.llm.ainvoke(prompt)
            logger.info("Generated async response from GigaChat")
            return response
        except Exception as e:
            logger.error(f"Error generating async response: {e}")
            raise

