from langchain_chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings


loader = TextLoader('./pragetx.md')
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=4000, chunk_overlap=4)
docs = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings()

chroma = Chroma.from_documents(docs, embeddings, persist_directory='./pragetx_chroma')