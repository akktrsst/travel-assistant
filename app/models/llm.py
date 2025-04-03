import os
from typing import List, Union
from huggingface_hub import InferenceClient
from ctransformers import AutoModelForCausalLM
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMHandler:
    def __init__(self):
        self.api_model = self._initialize_api_model()
        self.local_model = self._initialize_local_model()
        
    def _initialize_api_model(self):
        # Using HuggingFace's Inference API
        api_token = os.getenv("HF_API_TOKEN")
        if not api_token:
            raise ValueError("HF_API_TOKEN not found in environment variables")
        return InferenceClient(token=api_token)
    
    def _initialize_local_model(self):
        # Initialize local GGML model
        model_path = "models/llama-2-7b-chat.gguf"
        if os.path.exists(model_path):
            return AutoModelForCausalLM.from_pretrained(
                model_path,
                model_type="llama",
                max_new_tokens=512
            )
        return None

    def generate_response(self, message: str, context: List[dict]) -> str:
        # Try API model first, fallback to local if needed
        try:
            return self._generate_api_response(message, context)
        except Exception as e:
            if self.local_model:
                return self._generate_local_response(message, context)
            raise e

    def _generate_api_response(self, message: str, context: List[dict]) -> str:
        prompt = self._format_prompt(message, context)
        response = self.api_model.text_generation(
            prompt,
            model=os.getenv("DEFAULT_MODEL", "mistralai/Mistral-7B-Instruct-v0.1"),
            max_new_tokens=int(os.getenv("MAX_NEW_TOKENS", "512")),
            temperature=float(os.getenv("TEMPERATURE", "0.7"))
        )
        return response

    def _generate_local_response(self, message: str, context: List[dict]) -> str:
        prompt = self._format_prompt(message, context)
        response = self.local_model(prompt)
        return response

    def generate_itinerary(self, prompt: str) -> str:
        # Specialized method for itinerary generation
        try:
            return self._generate_api_response(prompt, [])
        except Exception as e:
            if self.local_model:
                return self._generate_local_response(prompt, [])
            raise e

    def _format_prompt(self, message: str, context: List[dict]) -> str:
        # Format the conversation context and current message
        formatted_context = "\n".join([
            f"User: {turn['user']}\nAssistant: {turn['assistant']}"
            for turn in context
        ])
        return f"{formatted_context}\nUser: {message}\nAssistant:" 