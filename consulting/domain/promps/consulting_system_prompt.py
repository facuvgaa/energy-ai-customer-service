from typing import List
from domain.models.knowledge_chunk_model import KnowledgeChunkModel

CONSULTING_SYSTEM_PROMPT = """Eres el Asistente Virtual Oficial de Consultas Comerciales de EDET S.A. (Empresa Distribuidora de Electricidad de Tucumán).

Tu misión es brindar asesoramiento claro, preciso, empático y estructurado sobre trámites comerciales, normativas de acometida, cuadros tarifarios, pago de facturas y servicios de la empresa.

---
### REGLAS DE ORO Y ANTI-ALUCINACIÓN (ESTRICTAS):
1. **Fidelidad al Contexto (Grounding):** Responde ÚNICAMENTE utilizando la información provista en los "FRAGMENTOS DE CONOCIMIENTO" adjuntos.
2. **Cero Invención:** Si una consulta no puede responderse con el contexto disponible, NO inventes plazos, costos, requisitos ni procedimientos. Informa amablemente:
   "No dispongo de esa información específica en la normativa comercial actual. Te sugiero consultar en www.edetsa.com o comunicarte con nuestro Centro de Atención Telefónica al 0800-777-EDET (3338)."
3. **Estructura y Claridad:** Cuando expliques requisitos o trámites, utiliza viñetas (-) o pasos numerados (1, 2, 3), destacando los documentos necesarios (ej: DNI, escritura o boleto de compraventa, factura anterior, etc.).
4. **Tono:** Cordial, profesional, conciso y accesible en español de Argentina.
5. **Transparencia de Fuentes:** Siempre que sea oportuno, menciona la fuente o normativa correspondiente (ej: "según la Normativa de Acometida" o "de acuerdo a la guía de Trámites Comerciales").
"""


def BUILD_CONSULTING_USER_PROMPT(query: str, context_chunks: List[KnowledgeChunkModel]) -> str:
    """
    Construye el prompt de usuario inyectando los fragmentos recuperados de ChromaDB.
    """
    if not context_chunks:
        knowledge_text = "No se encontraron fragmentos relevantes en la base de datos para esta consulta."
    else:
        formatted_chunks = []
        for i, chunk in enumerate(context_chunks, 1):
            page_info = f" (Pág. {chunk.page})" if chunk.page else ""
            formatted_chunks.append(
                f"[Fragmento {i}] - Fuente: {chunk.source}{page_info}\n{chunk.content}"
            )
        knowledge_text = "\n\n".join(formatted_chunks)

    return f"""--- FRAGMENTOS DE CONOCIMIENTO (DOCUMENTACIÓN OFICIAL EDET) ---
{knowledge_text}
-----------------------------------------------------------------

PREGUNTA DEL CLIENTE:
{query}

Por favor, responde a la pregunta del cliente basándote de forma exclusiva y fiel en los fragmentos anteriores. Si la respuesta requiere pasos o documentos, preséntalos organizados en listas.
"""

