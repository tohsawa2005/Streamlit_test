import os

import streamlit as st
# from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.callbacks import StreamlitCallbackHandler
# from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder

# load_dotenv()


def create_agent_chain():
    chat = ChatOpenAI(
        # openai_api_key = "ここに Keyを直接書いていた",
        openai_api_key = st.secrets.OpenAIAPI.openai_api_key,
        model_name = "gpt-3.5-turbo",       
        temperature = 0.5,
        streaming=True,
    )

    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }
    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

    tools = load_tools(["ddg-search", "wikipedia"])
    return initialize_agent(
        tools,
        chat,
        agent=AgentType.OPENAI_FUNCTIONS,
        agent_kwargs=agent_kwargs,
        memory=memory,
    )

if "agent_chain" not in st.session_state:
    st.session_state.agent_chain = create_agent_chain()


# タイトル表示
st.title("Welcome to Rakutive Concerge!")

mode = 1 #初期値
# サイドバー
st.sidebar.title("深掘りメニュー")
sel = st.sidebar.radio("以下から選択してください：", ("新しい質問", "なぜの深掘り", "どうしての深掘り", "母国との違いを深掘り", "続けて深掘り")
)

# サイドバー選択での処理

if sel == "新しい質問":
    # markdownをクリアする
    # タイトル下の表示
    st.write("May I help you?")
    mode = 1
    st.session_state.agent_chain = create_agent_chain()

elif sel == "なぜの深掘り":
    # タイトル下の表示
    st.write("これはなぜの深掘りです")
    mode = 2
    # 履歴にSystem Promptとして、なぜをつけてChatの回答を得る

elif sel == "どうしての深掘り":
    # タイトル下の表示
    st.write("これはどうしての深掘りです")
    mode = 2
    # 履歴にSystem Promptとして、どうしてをつけてChatの回答を得る

elif sel == "母国との違いを深掘り":
    # タイトル下の表示
    st.write("ベトナムとの違いを深掘りします")
    mode = 2
    # Chatを使って、System Prompotで命令して、母国との違いをMarkdownで回答する

elif sel == "続けて深掘り":
    # タイトル下の表示
    st.write("さらに深掘りしたい質問を入れてください")
    mode = 3
    # Chatを使って、履歴に質問を加えて、Chatの回答を得る


# ブラウザでのメイン部分の表示
if "messages" not in st.session_state or mode == 1:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 質問入力のプロセスの開始
# ブラウザの下部に入力エリアを作る
prompt = st.chat_input("質問をタイプしてください")

# 深掘りが2の時に、prompt_directとして、特定のプロンプトを入れる
if sel == "なぜの深掘り":
    prompt_direct = "これはなぜなんですか？"
elif sel == "どうしての深掘り":
    prompt_direct = "これはどうしてなんですか？"
elif sel == "母国との違いを深掘り":
    prompt_direct = "この説明のベトナムとの違いを文化や風習の視点から教えてもらえますか？"

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        callback = StreamlitCallbackHandler(st.container())
        response = st.session_state.agent_chain.run(prompt, callbacks=[callback])
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

if mode == 2:
    with st.chat_message("assistant"):
        # response = "いいてんきですね"

        callback = StreamlitCallbackHandler(st.container())
        response = st.session_state.agent_chain.run(prompt_direct, callbacks=[callback])
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})