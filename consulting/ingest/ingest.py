import os
from pathlib import Path
import chromadb
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai
from google.genai import types

from gemini_embeddig_function import GeminiEmbeddingFunction

# Cargar variables de entorno
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
from gemini_embeddig_function import GeminiEmbeddingFunction


load_dotenv(Path(__file__).resolve().parent.parent / ".env")
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY no encontrada en las variables de entorno.")

# Conexión con ChromaDB
chroma_host = os.getenv("CHROMA_HOST", "localhost")
chroma_port = int(os.getenv("CHROMA_PORT", 8000))

print(f"🔌 Conectando a ChromaDB en {chroma_host}:{chroma_port}...")
client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

gemini_ef = GeminiEmbeddingFunction(api_key=api_key)

collection = client.get_or_create_collection(
    name="edet_knowledge_base",
    embedding_function=gemini_ef,
)

# Text splitter para generar fragmentos
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""],
)

pdf_dir = Path(__file__).parent / "pdf_by_edet"
gemini_client = genai.Client(api_key=api_key)

all_docs = []
all_metadatas = []
all_ids = []

for pdf_path in sorted(pdf_dir.glob("*.pdf")):
    print(f"\n📄 Procesando: '{pdf_path.name}'...")
    reader = PdfReader(pdf_path)

    # 1. Intentamos extraer texto digital directamente con pypdf
    pdf_text = ""
    extracted_pages = []
    for page_idx, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        if page_text.strip():
            extracted_pages.append((page_idx + 1, page_text))
            pdf_text += page_text

    # 2. Si no tiene capa de texto digital (es afiche/infografía), usamos Gemini Vision
    if len(pdf_text.strip()) < 50:
        print("   🔍 Detectado como afiche/escaneo. Extrayendo texto completo con Gemini Vision...")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        resp = gemini_client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                "Extraé y transcribí de forma completa y detallada todo el texto, pasos, requisitos y trámites comerciales de este documento oficial de EDET en español.",
            ],
        )
        extracted_pages = [(1, resp.text)]

    # 3. Troceamos el texto y preparamos los metadatos
    pdf_chunks_count = 0
    for page_num, text_content in extracted_pages:
        chunks = splitter.split_text(text_content)
        for chunk_idx, chunk in enumerate(chunks):
            clean_stem = "".join(c if c.isalnum() else "_" for c in pdf_path.stem)
            chunk_id = f"{clean_stem}_p{page_num}_c{chunk_idx}"
            all_ids.append(chunk_id)
            all_docs.append(chunk)
            all_metadatas.append({
                "source": pdf_path.name,
                "page": page_num,
            })
            pdf_chunks_count += 1

    print(f"   ✅ Extraídos {pdf_chunks_count} fragmentos de '{pdf_path.name}'.")

# 4. Guardamos todo en ChromaDB
print(f"\n🚀 Subiendo {len(all_docs)} fragmentos a ChromaDB con embeddings de Gemini (3072 dimensiones)...")
collection.add(
    ids=all_ids,
    documents=all_docs,
    metadatas=all_metadatas,
)

print(f"\n🎉 ¡Ingesta completada exitosamente!")
print(f"📊 Total de documentos en la colección 'edet_knowledge_base': {collection.count()}")