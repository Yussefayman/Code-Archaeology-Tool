"""Configuration and LLM initialization."""

import os
from typing import Any, Dict
from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables.

    Returns:
        Configuration dictionary
    """
    load_dotenv()

    config = {
        "llm_provider": os.getenv("LLM_PROVIDER", "groq"),
        "llm_model": os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        "temperature": float(os.getenv("TEMPERATURE", "0.2")),
        "max_tokens": int(os.getenv("MAX_TOKENS", "4000")),
        "max_iterations": int(os.getenv("MAX_ITERATIONS", "5")),
        "repo_path": os.getenv("REPO_PATH", "."),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }

    return config


def get_llm(config: Dict[str, Any] = None) -> Any:
    """Get LLM instance based on configuration.

    Args:
        config: Optional configuration dictionary

    Returns:
        LLM instance

    Raises:
        ValueError: If provider is not supported or API key is missing
    """
    if config is None:
        config = load_config()

    provider = config["llm_provider"].lower()
    model = config["llm_model"]
    temperature = config["temperature"]
    max_tokens = config["max_tokens"]

    if provider == "groq":
        from langchain_groq import ChatGroq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment. "
                "Please set it in .env file or environment variables."
            )

        return ChatGroq(
            groq_api_key=api_key,
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. "
                "Please set it in .env file or environment variables."
            )

        return ChatOpenAI(
            openai_api_key=api_key,
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment. "
                "Please set it in .env file or environment variables."
            )

        return ChatAnthropic(
            anthropic_api_key=api_key,
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: groq, openai, anthropic"
        )
