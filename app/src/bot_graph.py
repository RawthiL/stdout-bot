from typing import Annotated

from langchain.chat_models import init_chat_model
from langchain_community.chat_models import ChatOpenAI
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from typing import Annotated,List,Literal
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder
from langgraph.graph.message import AnyMessage,add_messages,RemoveMessage

from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection



import os

PLAIN_MEMORY_LENGHT = 5
SUMMARY_TRIGGER = 15


class State(TypedDict):
    messages:Annotated[List[AnyMessage],add_messages]
    summary: str
    user_name: str


def build_model(model_endpoint, model_token, model_name):

    # Custom headers
    custom_headers = {
        'Authorization': model_token,
    }
    # OpenAI based client
    llm = ChatOpenAI(model=model_name,
                    api_key="...",
                    base_url=model_endpoint,
                    default_headers=custom_headers)
    # Build template for the model
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_message}"),
            MessagesPlaceholder("messages")
        ]
    )
    return prompt_template | llm



def build_graph(llm_model, postgresql_db_uri=None):
    graph_builder = StateGraph(State)

    def chat_node(state:State)->State:
        system_message=""
        if state["user_name"] is not None:
            system_message += f"The user is called \"{state["user_name"]}\"\n"
        summary = state.get("summary", "")
        if summary:
            system_message += f"Summary of previous interactions with user:\n{summary}"
        state["messages"]=llm_model.invoke(
                    {
                        "system_message":system_message,
                        "messages":state["messages"],
                    }
                )
        return state

    def summarize_conversation(state: State):
        summary = state.get("summary", "")
        system_message="You are a summarizer, your output should only contain the requested summary task, no introductory text."
        if summary:
            summary_message = (
                f"""Given this user chat summary:\n\n{summary}\n\nExtend the summary by taking into account these new messages:\n\n
                """
            )
        else:
            summary_message = "Create a summary of the following conversation:"
        response = llm_model.invoke(
            {
                "system_message":system_message,
                "messages":[HumanMessage(content=summary_message)]+state["messages"],
                }
            )
        # We now need to delete messages that we no longer want to show up # delete all message except last 2
        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-PLAIN_MEMORY_LENGHT]]

        return {"summary": response.content, "messages": delete_messages}

    def should_continue(state: State) -> Literal["summarize", END]:
        """Return the next node to execute."""
        messages = state["messages"]
        # If there are more than six messages, then we summarize the conversation
        if len(messages) > SUMMARY_TRIGGER:
            print("Summarizing!")
            return "summarize"
        return END

    graph_builder.add_node("chatnode",chat_node)
    graph_builder.add_node("summarize",summarize_conversation)
    graph_builder.add_edge(START,"chatnode")
    graph_builder.add_conditional_edges("chatnode",should_continue)
    graph_builder.add_edge("summarize",END)

    if postgresql_db_uri is not None:
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }
        conn = Connection.connect(postgresql_db_uri, **connection_kwargs)
        memory = PostgresSaver(conn)
        memory.setup()
    else:
        memory = InMemorySaver()
    
    return graph_builder.compile(checkpointer=memory)




def user_graph_interaction(graph, user_id, user_mesage, user_name=None):

    config = {"configurable": {"thread_id": str(user_id)}}

    # stream_graph_updates(user_input)
    input_state={"messages":[user_mesage], 
                 "user_name": user_name}
    response_state=graph.invoke(input_state,config=config)

    return response_state["messages"][-1].content





