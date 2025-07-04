import os

from google.oauth2 import service_account
from langchain_google_vertexai import VertexAI

if __name__ == '__main__':
    print(os.path.exists('./gcp_cred.json'))

    # サービスアカウントキーから認証情報を読み込み
    credentials = service_account.Credentials.from_service_account_file('./gcp_cred.json')

    model = VertexAI(generation_model='gemini-1.5-pro', credentials=credentials)
