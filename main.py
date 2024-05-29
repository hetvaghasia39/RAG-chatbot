import gradio as gr
import os
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
import re
import dotenv
from utils import HuggingChat
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
import langchain

# import json
# import shutil
# import magic
# import ollama
# from langchain_community.vectorstores.qdrant import Qdrant
# from langchain_core.documents import Document
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_community.chains import 
from langchain_community.chat_models import ChatOllama
# from hugchat import hugchat
# from langchain.callbacks import SystemMessage
# from hugchat.login import Login
langchain.debug = False

dotenv.load_dotenv()


class GradioApp:
    def __init__(self):
        self.history = []
        self.links = []
        

#         template = """
# You are a helpful health assistant. These Human will ask you a questions about their pregnancy health.
# Use following piece of context to answer the question.
# If you don't know the answer, just say you don't know.
# Keep the answer within 2 sentences and concise.

# Context: {context}
# Question: {question}
# Answer: """


        self.template = """
You are a helpful AI bot that guides the customer or user through the website content and provides the user with exact details they want.
You help everyone by answering questions, and improve your answers from previous answers in History.
Don't try to make up an answer, if you don't know, ask for more detail otherwise say you can contact the support team at https://pragetx.com/contact-us/
Answer in the same language the question was asked.
Answer in a way that is easy to understand.
Try to limit the answer to 3-4 sentences.
Provide source url as well at the end of the answer.
Do not say "Based on the information you provided, ..." or "I think the answer is...". Just answer the question directly in detail.

History: {chat_history}

Context: {context}

Question: {question}
Answer: 
"""
        self.prompt = PromptTemplate(
            template=self.template,
            input_variables=["chat_history","context", "question"]
        )
        self.db = Chroma(persist_directory="./pragetx_chroma", embedding_function=HuggingFaceEmbeddings(), collection_name="pragetx")  
        # self.llm = ChatOllama(model="phi3:3.8b", base_url="http://localhost:11434", num_gpu=16)
        self.llm = HuggingChat(email = os.getenv("HF_EMAIL") , psw = os.getenv("HF_PASS") )
        self.chain = (
            {"chat_history": self.chat_history, "context": self.db.as_retriever(search_kwargs={"k":3}), "question": RunnablePassthrough()} |
            self.prompt |
            self.llm | 
            StrOutputParser())
    def chat_history(self, history):
        print(self.history)
        print("\n".join(f"##Human: {x[0]}\n{'##Bot: '+x[1] if x[1] else ''}" for x in self.history))
        return "\n".join(f"##Human: {x[0]}\n{'##Bot: '+x[1] if x[1] else ''}" for x in self.history)

    def user(self,user_message, history):
        self.history = history + [[user_message, None]]
        return "", history + [[user_message, None]]
    
    def bot(self,history):
        print(history)
        prompt = history[-1][0] or ""
        for chunks in self.chain.stream(prompt):
            history[-1][1] = history[-1][1] or ""
            history[-1][1] += chunks
            yield history
        history[-1][1] = history[-1][1] or ""
        self.history = history
        # extract links in the response and store them
        links = re.findall(r'(https?://\S+)', history[-1][1])
        print(links)
        self.links = links
        print(history[-1][1])
        print(history)
        
    # def list_links(self):
    #     print( "link_buttons", self.links)
    #     link_buttons = []
    #     for link in range(5):
    #         if link < len(self.links):
    #             btn = gr.Button(f"Open {self.links[link]}", visible=True)
                
    #         else:
    #             btn = gr.Button(visible=False)
    #         link_buttons.append(btn)
    #     return link_buttons
        


with gr.Blocks() as demo:
    gradio_app = GradioApp()
    # link_buttons = []
    # files = gr.Files(label="Upload Documents and Medical Reports", type="filepath", file_types=["pdf", "docx", "jpg", "jpeg", "png"])
    # upload_button = gr.UploadButton(label="Upload Documents and Medical Reports", type="filepath", file_count='multiple', file_types=["pdf", "docx", "jpg", "jpeg", "png"], )
    output_text = gr.Markdown(label="Output", value="   ")
    infer_status = gr.Label("Infer Status: ", visible=False)

    # upload_button.upload(gradio_app.upload_files, upload_button, [files, output_text])
    chatbot = gr.Chatbot()
    # with gr.Row():
    #     for link in range(5):
    #         btn = gr.Button(visible=False)
    #         link_buttons.append(btn)
    msg = gr.Textbox()
    clear = gr.Button("Clear")
    # for link in range(5):
    #     print(gradio_app.links)
    #     btn.click(lambda: None, None, None, js=f"window.location.assign('{gradio_app.links[link]}');" if link < len(gradio_app.links) else None)
    msg.submit(gradio_app.user, [msg, chatbot], [msg, chatbot], queue=False).then(
      gradio_app.bot, chatbot, chatbot
    )
    # .then(
    #     gradio_app.list_links, None, link_buttons
    # )
    clear.click(lambda: None, None, chatbot, queue=False)
demo.queue()
demo.launch(share=True, server_name="0.0.0.0", root_path="/bot")
