import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import openai
import streamlit as st
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.tools import YouTubeSearchTool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.agents import AgentExecutor, create_json_chat_agent, Tool
from langchain.schema import SystemMessage
from dotenv import dotenv_values

# Load environment variables
config = dotenv_values(".env")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=config["SPOTIFY_CLIENT_ID"],
        client_secret=config["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=config["SPOTIFY_REDIRECT_URI"],
        scope="user-library-read user-top-read playlist-modify-private playlist-modify-public",
    )
)

current_user = sp.current_user()

assert current_user is not None

print(current_user["id"], "token saved in '.cache' file.")

# Define the prompt
prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content="You are a chatbot having a conversation with a human. You love making references to French culture in your answers."
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{human_input}"),
    ]
)

# Initialize memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Chat Template
system = """
You are designed to solve tasks. Each task requires multiple steps that are represented by a markdown code snippet of a json blob.
The json structure should contain the following keys:
thought -> your thoughts
action -> name of a tool
action_input -> parameters to send to the tool

These are the tools you can use: {tool_names}.

These are the tools descriptions:

{tools}

If you have enough information to answer the query use the tool "Final Answer". Its parameters is the solution.
If there is not enough information, keep trying.
"""

human = """
Add the word "STOP" after each markdown snippet. Example:

```json
{{"thought": "<your thoughts>",
 "action": "<tool name or Final Answer to give a final answer>",
 "action_input": "<tool parameters or the final output"}}
STOP

This is my query="{input}". Write only the next step needed to solve it.
Your answer should be based in the previous tools executions, even if you think you know the answer.
Remember to add STOP after each snippet.

These were the previous steps given to solve this query and the information you already gathered:
"""

chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", human),
        MessagesPlaceholder("agent_scratchpad")
    ]
)

# Define Tools
class SpotifyTool:
    def __init__(self, sp):
        self.sp = sp

    def run(self, question=None):
        results = self.sp.current_user_saved_tracks(limit=30)
        top_tracks = [
            {
                'name': track['track']['name'],
                'link': track['track']['external_urls']['spotify']
            }
            for track in results['items']
        ]
        return top_tracks

# Initialize wrappers
youtube_search_tool = YouTubeSearchTool()
spotify_tool_instance = SpotifyTool(sp)

# Set your OpenAI API key securely
openai.api_key = config['OPENAI_API_KEY']
llm = ChatOpenAI(api_key=openai.api_key, model="gpt-4o")  # Correct initialization

# Initialize Tools
spotify_tool = Tool(
    name="Spotify Tool",
    description="You are a mental health assistant. You aim to make the user happy. Always suggest between 3 to 5 songs and not more than that unless the user asks for more. The output should strictly be in json format.",
    func=spotify_tool_instance.run
)

youtube_tool = Tool(
    name="YouTube",
    description="You are a mental health assistant. Suggest relevant videos on YouTube. Your goal is to improve the user's mood.",
    func=youtube_search_tool.run
)

tools = [spotify_tool, youtube_tool]

agent = create_json_chat_agent(
    tools=tools,
    llm=llm,
    prompt=chat_template,
    stop_sequence=["STOP"],
    template_tool_response="{observation}"
)

chat_history = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent_interact = AgentExecutor(agent=agent,
                               tools=tools,
                               verbose=True,
                               handle_parsing_errors=True)

# Streamlit UI
st.set_page_config(page_title="SailBuddy", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main {
        background-color: #000000;
    }
    .stButton>button {
        background-color: #004d40;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        transition-duration: 0.4s;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: white;
        color: #004d40;
        border: 2px solid #004d40;
    }
    .stTextInput>div>input {
        padding: 10px;
        font-size: 16px;
        border: 2px solid #004d40;
        color: white;
        background-color: #000000;
    }
    .stMarkdown h1, h2, h3, h4, h5, h6 {
        color: #4CAF50;
    }
    .stMarkdown ul {
        list-style-type: none;
    }
    .stMarkdown li:before {
        content: "\\1F4B2";
        color: #4CAF50;
        padding-right: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("⛵ SailBuddy")
st.write("### Enter your query for Spotify or YouTube to get song and video recommendations:")

query = st.text_input("Query", placeholder="Enter query for Spotify top tracks or YouTube videos")

if st.button("Submit Query"):
    response = agent_interact.invoke({"input": query})
    
    # Debug: print the entire response to see its structure
    print("Response:", response)
    if "output" in response:
        output = response["output"]
        for key, value in output.items():
            st.subheader(f"⚓ {key.capitalize()} ⚓")  # Use subheader for keys with nautical emojis for better UI
            if isinstance(value, list):  # If the value is a list, iterate over its items
                for item in value:
                    if isinstance(item, dict):  # If the item is a dictionary, display its key-value pairs
                        link = item.get('link', '#')
                        name = item.get('name', 'Unknown')
                        st.markdown(f"- [{name}]({link})", unsafe_allow_html=True)
                    else:  # If the item is not a dictionary, display it directly
                        st.markdown(f"- {item}", unsafe_allow_html=True)
            else:  # If the value is not a list, display it directly
                st.markdown(f"**{key.capitalize()}**: {value}", unsafe_allow_html=True)
    else:
        st.write("No output available.")
