from google.oauth2 import service_account
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the application.
    """

    OPENAI_API_KEY: str = Field(
        default='',
        description='OpenAI API key for accessing OpenAI services.',
        examples=['sk-...'],
    )
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(
        default='',
        description='Path to the Google Cloud service account key file.',
        examples=['/path/to/service_account.json'],
    )
    GOOGLE_CLOUD_PROJECT: str = Field(
        default='',
        description='Google Cloud project ID for accessing Google services.',
        examples=['my-gcp-project'],
    )
    LANGCHAIN_TRACING_V2: bool = Field(
        default=False,
        description='Enable LangChain tracing for debugging and monitoring.',
        examples=[True, False],
    )
    LANGCHAIN_API_KEY: str = Field(
        default='',
        description='API key for LangChain services.',
        examples=['langchain-...'],
    )
    LANGCHAIN_PROJECT: str = Field(
        default='default',
        description='LangChain project name for organizing resources.',
        examples=['my-langchain-project'],
    )

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


config = Settings()

google_credentials = (
    service_account.Credentials.from_service_account_file(config.GOOGLE_APPLICATION_CREDENTIALS)
    if config.GOOGLE_APPLICATION_CREDENTIALS
    else None
)
