from pathlib import Path
import streamlit as st
from streamlit_chat import message
from huggingface_hub import InferenceClient
from langchain import HuggingFaceHub
import requests# Internal usage
import os
from dotenv import load_dotenv
from time import sleep
import uuid
import sys
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

st.set_page_config(page_title="AI Chatbot 100% Free", layout="wide")
st.write('完全开源免费的AI智能聊天助手 | Absolute Free & Opensouce AI Chatbot')

css_file = "main.css"
with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

load_dotenv()
yourHFtoken = os.getenv("HUGGINGFACEHUB_API_TOKEN")
repo_id=os.getenv("repo_id")

#AVATARS
#av_us = './man.png' #"🦖" #A single emoji, e.g. "🧑 💻", "🤖", "🦖". Shortco
#av_ass = './robot.png'
av_us = '🧑'
av_ass = '🤖'

def starchat(model,myprompt, your_template):
    from langchain import PromptTemplate, LLMChain
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = yourHFtoken
    llm = HuggingFaceHub(repo_id=model,
                         model_kwargs={"min_length":100,
                                       "max_new_tokens":1024, "do_sample":True,
                                       "temperature":0.1,
                                       "top_k":50,
                                       "top_p":0.95, "eos_token_id":49155})     
    #my_prompt_template = """
    #<<SYS>>You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
    #If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
    #In each conversation, question is placed after [INST] while your answer should be placed after [/INST]. By looking [INST] and [/INST], you must consider multi-turn conversations saved in {contexts}.<</SYS>>
    #[INST] {myprompt} [/INST] 
    #assistant:
   # """    
    my_prompt_template = """assistant is helpful, respectful and honest. assistant always answer as helpfully as possible, while being safe. assistant's answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. assistant should ensure assistant's responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If assistant doesn't know the answer to a question, please don't share false information. Converstation history is saved as {contexts} for assistant to reference before making a final response to current user question as {myprompt}. Keep in mind, if assistant finds Converstation history not helpful in responding to current user question, just ignore Converstation history and proceed to response to current user question as a standalone question. assistant should only output the essential contents of the response, do not output any unmeaningful information. Unmeaningful information includes but not limited to the following:
    - "I have referenced the Converstation history." or similar statements.
    - any part of the Converstation history.
    - information in a format such as: user:... assistant: ..., i.e. do not use such format.
    - response with more than one language, i.e. do not response in more than 1 language unless VERY necessary. Reponse in the language as user question or as user asks assistant to use.
    - any information not related to current quesiton.
    - when user says "you", normally it means assistant, so assistant should take designated roles accordingly.
    """
    template = my_prompt_template    
    prompt = PromptTemplate(template=template, input_variables=["contexts", "myprompt"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
   # add_notes_1="Beginning of chat history:\n"
   # add_notes_2="End of chat history.\n"
   # add_notes_3="Please consult the above chat history before responding to the user question below.\n"
   # add_notes_4="User question: "
   # myprompt_temp=myprompt
   # myprompt = add_notes_1 + "\n" + contexts + "\n" + add_notes_2 + "\n" + add_notes_3 + "\n"+ add_notes_4 + "\n" + myprompt
   # llm_reply = llm_chain.run(myprompt)
    llm_reply = llm_chain.run({'contexts': contexts, 'myprompt': myprompt})  
    reply = llm_reply.partition('<|end|>')[0]    
    return reply

if "file_name" not in st.session_state:
    st.session_state["file_name"] = str(uuid.uuid4()) + ".txt"    

def writehistory(text):           
    with open(st.session_state["file_name"], 'a+') as f:
        f.write(text)
        f.write('\n')
        f.seek(0) 
        contexts = f.read()        
    return contexts

if "messages" not in st.session_state:
   st.session_state.messages = []
for message in st.session_state.messages:
   if message["role"] == "user":
#      with st.chat_message(message["role"],avatar=av_us):
      with st.chat_message(message["role"]):                  
           st.markdown(message["content"])           
   else:
#       with st.chat_message(message["role"],avatar=av_ass):
       with st.chat_message(message["role"]):                   
           st.markdown(message["content"])           

if myprompt := st.chat_input("Enter your question here."):    
    st.session_state.messages.append({"role": "user", "content": myprompt})    
#    with st.chat_message("user", avatar=av_us):
    with st.chat_message("user"):        
        st.markdown(myprompt)        
        usertext = f"user: {myprompt}"              
        contexts = writehistory(usertext)          
    with st.chat_message("assistant"):
        with st.spinner("AI Thinking..."):                        
            message_placeholder = st.empty() 
            full_response = ""            
            res = starchat(
#                  st.session_state["hf_model"],
                  repo_id,
                  myprompt, "<|system|>\n<|end|>\n<|user|>\n{myprompt}<|end|>\n<|assistant|>")            
            response = res.split(" ")            
            for r in response:
                full_response = full_response + r + " "
                message_placeholder.markdown(full_response + "|")
                sleep(0.1)                       
            message_placeholder.markdown(full_response)            
            asstext = f"assistant: {full_response}"             
            contexts = writehistory(asstext)            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
