import os
from google import genai
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings


class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def __call__(self, input: Documents) -> Embeddings:
        if not input:
            return []

        embeddings = []
        # Gemini maneja batches cómodamente en bloques de 50 textos
        batch_size = 50
        for i in range(0, len(input), batch_size):
            batch = input[i : i + batch_size]
            response = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=batch,
            )
            for e in response.embeddings:
                embeddings.append(e.values)

        return embeddings
