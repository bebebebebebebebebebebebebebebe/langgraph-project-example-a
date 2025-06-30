from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chatbot(state: State):
    return {'messages': [('assistant', "Hello! I'm a simple LangGraph chatbot.")]}


def create_graph():
    workflow = StateGraph(State)
    workflow.add_node('chatbot', chatbot)
    workflow.add_edge(START, 'chatbot')
    workflow.add_edge('chatbot', END)
    return workflow.compile()


graph = create_graph()
