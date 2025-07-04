from google.oauth2 import service_account
from langchain_google_vertexai import ChatVertexAI
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .example_graph import chatbot


class GraphConfig(BaseSettings):
    """
    Configuration settings for the simple chatbot graph.
    """

    VERSION: str = '0.1.0'
    NAME: str = 'simple_chatbot_graph'
    DESCRIPTION: str = 'A simple chatbot graph using LangGraph and LangChain.'
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(
        default='./gcp_cred.json',
        description='Path to the Google Cloud service account key file.',
        examples=['./gcp_cred.json', '/path/to/your/service-account-key.json'],
    )
    GOOGLE_VERTEXAI_GENERATION_MODEL: str = Field(
        default='gemini-1.5-pro',
        description='The Google Vertex AI generation model to use.',
        examples=['gemini-1.5-flash', 'gemini-1.5-pro'],
    )
    GOOGLE_CLOUD_PROJECT: str = Field(
        default='technical-research-452606',
        description='Google Cloud project ID.',
        examples=['technical-research-452606', 'my-project-id'],
    )

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


config = GraphConfig()


def main():
    print(config.GOOGLE_APPLICATION_CREDENTIALS)
    credentials = service_account.Credentials.from_service_account_file(config.GOOGLE_APPLICATION_CREDENTIALS)
    model = ChatVertexAI(
        model_name='gemini-2.0-flash-001',
        credentials=credentials,
    )
    response = model.invoke(
        [
            {
                'role': 'user',
                'content': '自己紹介をしてくれますか？',
            }
        ]
    )
    print(response.content)


if __name__ == '__main__':
    main()
