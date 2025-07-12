from typing import Annotated, TypedDict

from google.oauth2 import service_account
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import add_messages

# 認証情報を設定
credentials = service_account.Credentials.from_service_account_file('./gcp_cred.json')

# Vertex AIモデルを初期化
llm = ChatVertexAI(
    model_name='gemini-2.0-flash',
    credentials=credentials,
    project='technical-research-452606',
)

parser = StrOutputParser()

chain = llm | parser


def chatbot(state: MessagesState) -> MessagesState:
    response = chain.invoke(state['messages'])
    return {'messages': [AIMessage(content=response)]}


# グラフを定義
graph = StateGraph(MessagesState)
graph.add_node('chatbot', chatbot)
graph.add_edge(START, 'chatbot')
graph.add_edge('chatbot', END)

# コンパイル
app = graph.compile()
