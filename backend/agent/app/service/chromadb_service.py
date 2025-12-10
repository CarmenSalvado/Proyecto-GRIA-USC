from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


class ChromaDBService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.doc_path = "./app/service/documents"
        self.persist_directory = "./app/service/chroma_db"
        
    def crearDB(self):
        # Cargar documentos desde la carpeta ./documents
        loader = DirectoryLoader(self.doc_path, glob="**/*.md", show_progress=True)

        documentos = loader.load()
        if not documentos:
            print("No se encontraron documentos para cargar. Saliendo.")
            return
        print(f"Documentos cargados: {len(documentos)}")

        print("Creando y guardando vectorstore... Esto puede tardar.")
        # Dividir documentos en fragmentos más pequeños
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
        chunks = text_splitter.split_documents(documentos)
        print(f"Documentos divididos en {len(chunks)} fragmentos")
        
        # Creamos vectorstore
        print("Creando y guardando vectorstore... Esto puede tardar.")
        self.vector_store = Chroma.from_documents(
            documents = chunks,
            embedding = self.embeddings,
            persist_directory = self.persist_directory
        )

        print("Vectorstore creado y listo para usar")

if __name__ == "__main__":   
    ChromaDBService().crearDB()