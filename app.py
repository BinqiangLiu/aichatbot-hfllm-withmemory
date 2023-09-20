#Memory in prompt.
from pathlib import Path
import streamlit as st
#from streamlit_chat import message
from huggingface_hub import InferenceClient
from langchain import HuggingFaceHub
import requests# Internal usage
import os
from dotenv import load_dotenv
from time import sleep
#from hugchat import hugchat
#from hugchat.login import Login
#from streamlit_extras.colored_header import colored_header
#from streamlit_extras.add_vertical_space import add_vertical_space

st.set_page_config(page_title="AI Chatbot 100% Free", layout="wide")
st.write('完全开源免费的AI智能聊天助手 | Absolute Free & Opensouce AI Chatbot')

# --- PATH SETTINGS ---
css_file = "main.css"
# --- LOAD CSS, PDF & PROFIL PIC ---
with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

load_dotenv()
yourHFtoken = "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"
yourHFtoken = os.getenv("HUGGINGFACEHUB_API_TOKEN")
repo="HuggingFaceH4/starchat-beta"

#AVATARS
#av_us = './man.png' #"🦖" #A single emoji, e.g. "🧑 💻", "🤖", "🦖". Shortco
#av_ass = './robot.png'
av_us = '🧑'
av_ass = '🤖'
# Set a default model
if "hf_model" not in st.session_state:
    st.session_state["hf_model"] = "HuggingFaceH4/starchat-beta"

### INITIALIZING STARCHAT FUNCTION MODEL
def starchat(model,myprompt, your_template):
    from langchain import PromptTemplate, LLMChain
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = yourHFtoken
    llm = HuggingFaceHub(repo_id=model,
                         model_kwargs={"min_length":100,
                                       "max_new_tokens":1024, "do_sample":True,
                                       "temperature":0.1,
                                       "top_k":50,
                                       "top_p":0.95, "eos_token_id":49155})
#以下是新增内容
    my_prompt_template = """You are a very smart and helpful AI assistant. You are provided {contexts} as chat history between the user and you. For any following question, you MUST consider the chat history and response to {myprompt} as the user question.
    However, you SHOULD NOT limit your reponse to the chat history. In addition, you should take any actions you would take when you response to a user question normally
    And output your RESPONSE ONLY, do NOT OUTPUT the chat history or ANY unrelated information!
    AI Repsonse:
    """
#以上是新增内容    
    template = my_prompt_template
#    template = your_template
    prompt = PromptTemplate(template=template, input_variables=["contexts", "myprompt"])
#    prompt = PromptTemplate(template=template, input_variables=["myprompt"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
#    llm_reply = llm_chain.run(myprompt)
    llm_reply = llm_chain.run({'contexts': contexts, 'myprompt': myprompt})    
    reply = llm_reply.partition('<|end|>')[0]
    return reply

# FUNCTION TO LOG ALL CHAT MESSAGES INTO chathistory.txt
#def writehistory(text):
#    with open('chathistory.txt', 'a') as f:
#        f.write(text)
#        f.write('\n')
#增加下面一行代码，读取对话记录text并存储到contexts
#        contexts = f.read()
#    f.close()

def writehistory(text):
    with open('chathistory.txt', 'a+') as f:
        f.write(text)
        f.write('\n')
        f.seek(0)  # 将文件指针移动到文件开头
        contexts = f.read()
    return contexts

### START STREAMLIT UI
#st.title("🤗 HuggingFace Free ChatBot")
#st.subheader("using Starchat-beta")

# Initialize chat history
if "messages" not in st.session_state:
   st.session_state.messages = []
# Display chat messages from history on app rerun
for message in st.session_state.messages:
   if message["role"] == "user":
#      with st.chat_message(message["role"],avatar=av_us):
      with st.chat_message(message["role"]):
           st.markdown(message["content"])
   else:
#       with st.chat_message(message["role"],avatar=av_ass):
       with st.chat_message(message["role"]):
           st.markdown(message["content"])

# Accept user input
if myprompt := st.chat_input("Enter your question here."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": myprompt})
    # Display user message in chat message container
#    with st.chat_message("user", avatar=av_us):
    with st.chat_message("user"):
        st.markdown(myprompt)
        usertext = f"user: {myprompt}"
#        writehistory(usertext)
#新增如下一行        
        contexts = writehistory(usertext)
        # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("AI Thinking..."):
            message_placeholder = st.empty()
            full_response = ""
            res = starchat(
                  st.session_state["hf_model"],
                  myprompt, "<|system|>\n<|end|>\n<|user|>\n{myprompt}<|end|>\n<|assistant|>")
            response = res.split(" ")
            for r in response:
                full_response = full_response + r + " "
                message_placeholder.markdown(full_response + "▌")
                sleep(0.1)
            message_placeholder.markdown(full_response)
            asstext = f"assistant: {full_response}"
#            writehistory(asstext)
#新增如下一行        
            contexts = writehistory(asstext)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
