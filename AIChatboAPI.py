from flask import Flask, request, jsonify
from pathlib import Path
import streamlit as st
from streamlit_chat import message
from huggingface_hub import InferenceClient
from langchain import HuggingFaceHub
import requests
import os
from dotenv import load_dotenv
from time import sleep
import uuid
import sys
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from langchain import PromptTemplate, LLMChain

app = Flask(__name__)

load_dotenv()
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
repo_id = os.getenv("repo_id")
port = os.getenv('port')

def starchat(model, myprompt): 
    llm = HuggingFaceHub(repo_id=model,
                         model_kwargs={"min_length":1024,
                                       "max_new_tokens":5632, "do_sample":True,
                                       "temperature":0.1,
                                       "top_k":50,
                                       "top_p":0.95, "eos_token_id":49155})     
    my_prompt_template = """
    <<SYS>>You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
    If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
    In each conversation, question is placed after [INST] while your answer should be placed after [/INST]. By looking [INST] and [/INST], you must consider multi-turn conversations saved in {contexts}.<</SYS>>
    [INST] {myprompt} [/INST] 
    assistant:
    """    
    template = my_prompt_template    
    prompt = PromptTemplate(template=template, input_variables=["contexts", "myprompt"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    llm_reply = llm_chain.run({'contexts': contexts, 'myprompt': myprompt})  
    reply = llm_reply.partition('<|end|>')[0]    
    return reply

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    myprompt = data['prompt']
    
    # AI Chatbot logic
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
            with st.chat_message(message["role"]):                  
                st.markdown(message["content"])           
        else:
            with st.chat_message(message["role"]):                   
                st.markdown(message["content"])           

    st.session_state.messages.append({"role": "user", "content": myprompt})    
    with st.chat_message("user"):        
        st.markdown(myprompt)        
        usertext = f"user: {myprompt}"              
        contexts = writehistory(usertext)          
    with st.chat_message("assistant"):
        with st.spinner("AI Thinking..."):                        
            message_placeholder = st.empty() 
            full_response = ""            
            res = starchat(repo_id, myprompt)       
            response = res.split(" ")            
            for r in response:
                full_response = full_response + r + " "
                message_placeholder.markdown(full_response + "|")
                sleep(0.1)                       
            message_placeholder.markdown(full_response)            
            asstext = f"assistant: {full_response}"             
            contexts = writehistory(asstext)            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

    response = {
        'message': 'AI Chatbot response',
        'prompt': myprompt,
        'reply': full_response
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)