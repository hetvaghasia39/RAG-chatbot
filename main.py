import gradio as gr
import json
import os
import shutil
# import magic
# import ollama
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# from langchain_community.chains import 
from langchain_community.chat_models import ChatOllama
from langchain_chroma import Chroma
from hugchat import hugchat
from hugchat.login import Login
import dotenv
from utils import HuggingChat
from langchain import PromptTemplate

dotenv.load_dotenv()


class GradioApp:
    def __init__(self):
        # self.llm = ChatOllama(model="phi3:3.8b", base_url="http://localhost:11434", num_gpu=32)
        

        template = """
        You are a helpful health assistant. These Human will ask you a questions about their pregnancy health.
        Use following piece of context to answer the question.
        If you don't know the answer, just say you don't know.
        Keep the answer within 2 sentences and concise.

        Context: {context}
        Question: {question}
        Answer:

        """

        self.llm = HuggingChat(email = os.getenv("HF_EMAIL") , psw = os.getenv("HF_PASS") )
        self.chain = (self.llm | StrOutputParser())

    def user(self,user_message, history):
        return "", history + [[user_message, None]]
    
    def bot(self,history):
        print(history)
        prompt = history[-1][0] or ""
        for chunks in self.chain.stream(prompt):
            history[-1][1] = history[-1][1] or ""
            history[-1][1] += chunks
            yield history
        history[-1][1] = history[-1][1] or ""
        history[-1][1] += self.chain.invoke(prompt)
        print(history[-1][1])
        print(history)
        return history


with gr.Blocks() as demo:
    gradio_app = GradioApp()
    # files = gr.Files(label="Upload Documents and Medical Reports", type="filepath", file_types=["pdf", "docx", "jpg", "jpeg", "png"])
    # upload_button = gr.UploadButton(label="Upload Documents and Medical Reports", type="filepath", file_count='multiple', file_types=["pdf", "docx", "jpg", "jpeg", "png"], )
    output_text = gr.Markdown(label="Output", value="   ")
    infer_status = gr.Label("Infer Status: ", visible=False)


    # upload_button.upload(gradio_app.upload_files, upload_button, [files, output_text])
    chatbot = gr.Chatbot()  
    msg = gr.Textbox()
    clear = gr.Button("Clear")
    msg.submit(gradio_app.user, [msg, chatbot], [msg, chatbot], queue=False).then(
      gradio_app.bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

            
# demo.queue()
demo.launch(share=True)
