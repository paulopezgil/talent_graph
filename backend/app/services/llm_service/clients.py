from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import settings


def get_llm(temperature: float = 0) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_model,
        temperature=temperature,
        openai_api_key=settings.openai_api_key.get_secret_value(),
    )


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(openai_api_key=settings.openai_api_key.get_secret_value())
