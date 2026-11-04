from domain.port.knowledge_retriever_port import KnowledgeRetrieverPort
from dotenv import load_dotenv
from typing import Optional
import chromadb
from infrastructure.adapter_retriever.gemini_embedding_function import GeminiEmbeddingFunction
import os
from domain.models.knowledge_chunk_model import KnowledgeChunkModel
from typing import List
load_dotenv()


class ChromaKnowledgeRetrieverAdapter(KnowledgeRetrieverPort):
    def __init__(
            self, 
            host: Optional[str] = None,
            port: Optional[int] = None,
            collection_name: str = "edet_knowledge_base",
            embedding_function = None,
        ):

        self._host = host or os.getenv("CHROMA_HOST", "localhost")
        self._port = port or int(os.getenv("CHROMA_PORT", 8000))
        self._collection_name = collection_name
        api_key = os.getenv("GEMINI_API_KEY")
        self._embedding_fn = embedding_function or GeminiEmbeddingFunction(api_key=api_key)

        self._client = chromadb.HttpClient(host=self._host, port=self._port)
        self._collection = self._client.get_collection(
            name=self._collection_name,
            embedding_function=self._embedding_fn,
        )
    async def retrieve(self, query: str, limit: int = 4)-> List[KnowledgeChunkModel]:
        results = self._collection.query(
            query_texts= [query],
            n_results=limit
        )

        chunks = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas",[[]])[0]

        for doc, meta in zip(documents, metadatas):
            chunks.append(
                KnowledgeChunkModel(
                    content=doc,
                    source=meta.get("source", "Desconocido"),
                    page=meta.get("page"),
                )
            )

        return chunks