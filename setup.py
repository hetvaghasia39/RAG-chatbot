from langchain_chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

# get all files in pragetx_scraper/data
import os
import glob
import shutil
# get all files in pragetx_scraper/data
files = glob.glob('pragetx_scraper/data/*.md')

# check if folder named pragetx_chroma exists
if os.path.exists('pragetx_chroma'):
    shutil.rmtree('pragetx_chroma')
chroma = Chroma(persist_directory='./pragetx_chroma', embedding_function=HuggingFaceEmbeddings(), collection_name='pragetx')
for file in files:
    print(f'Processing {file}')
    loader = TextLoader(file)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=4)
    docs = text_splitter.split_documents(documents)
    url = None
    with open(file, 'r') as f:
        text = f.read()
        # url is in first line of the file in # <url> format
        url = text.split('\n')[0].replace('# ', '')
    for idx, text in enumerate(docs):
        # print(f'Processing document {idx}')
        # print(text.page_content)
        # print(docs[idx].metadata)
        docs[idx].metadata['url'] = url
        print(docs[idx].metadata)
    chroma.add_documents(docs)