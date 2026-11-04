import pytest
from unittest.mock import AsyncMock

from application.commands.command import Command
from application.use_case.process_consulting_message import ProcessConsultingMessage
from domain.models.consulting_context_model import ConsultingContextModel
from domain.models.knowledge_chunk_model import KnowledgeChunkModel
from domain.models.consulting_result_model import ConsultingResultModel
from domain.port.consulting_context_repository_port import ConsultingContextRepositoryPort
from domain.port.consulting_llm_port import ConsultingLlmPort
from domain.port.knowledge_retriever_port import KnowledgeRetrieverPort


@pytest.mark.asyncio
async def test_process_consulting_message_new_session():
    # 1. Mocks de los puertos de dominio
    mock_context_repo = AsyncMock(spec=ConsultingContextRepositoryPort)
    mock_retriever = AsyncMock(spec=KnowledgeRetrieverPort)
    mock_llm = AsyncMock(spec=ConsultingLlmPort)

    mock_context_repo.get_by_session.return_value = None

    mock_retriever.retrieve.return_value = [
        KnowledgeChunkModel(
            content="Para alta de nuevo suministro residencial se requiere escritura o boleto de compraventa y DNI.",
            source="TRAMITES COMERCIALES.pdf",
            page=2,
        )
    ]

    mock_llm.generate_response.return_value = ConsultingResultModel(
        response_text="Para solicitar el alta residencial necesitás presentar DNI y escritura o boleto de compraventa.",
        sources=["TRAMITES COMERCIALES.pdf"],
    )

    # 2. Instanciamos el caso de uso
    use_case = ProcessConsultingMessage(
        consulting_context=mock_context_repo,
        consulting_llm=mock_llm,
        knowledge=mock_retriever,
    )

    command = Command(
        session_id="session-test-001",
        user_id="user-123",
        content="¿Qué necesito para pedir el alta de luz?",
    )

    # 3. Ejecución
    response = await use_case.execute(command)

    # 4. Verificaciones
    assert "DNI y escritura" in response
    mock_context_repo.get_by_session.assert_awaited_once_with("session-test-001")
    mock_retriever.retrieve.assert_awaited_once_with(query="¿Qué necesito para pedir el alta de luz?", limit=4)
    mock_llm.generate_response.assert_awaited_once()
    mock_context_repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_consulting_message_existing_session():
    mock_context_repo = AsyncMock(spec=ConsultingContextRepositoryPort)
    mock_retriever = AsyncMock(spec=KnowledgeRetrieverPort)
    mock_llm = AsyncMock(spec=ConsultingLlmPort)

    existing_context = ConsultingContextModel(
        session_id="session-test-002",
        user_id="user-456",
        messages=[
            {"role": "user", "content": "Hola"},
            {"role": "assistant", "content": "¡Hola! Soy el asistente de EDET, ¿en qué puedo ayudarte?"},
        ],
    )
    mock_context_repo.get_by_session.return_value = existing_context
    mock_retriever.retrieve.return_value = []
    mock_llm.generate_response.return_value = ConsultingResultModel(
        response_text="El cambio de titularidad es sin costo administrativo.",
        sources=["TRAMITES COMERCIALES.pdf"],
    )

    use_case = ProcessConsultingMessage(
        consulting_context=mock_context_repo,
        consulting_llm=mock_llm,
        knowledge=mock_retriever,
    )

    command = Command(
        session_id="session-test-002",
        user_id="user-456",
        content="¿Tiene costo el trámite?",
    )

    response = await use_case.execute(command)

    assert response == "El cambio de titularidad es sin costo administrativo."
    # El historial previo de 2 mensajes ahora debe tener 4
    assert len(existing_context.messages) == 4
    assert existing_context.messages[2]["role"] == "user"
    assert existing_context.messages[2]["content"] == "¿Tiene costo el trámite?"
    assert existing_context.messages[3]["role"] == "assistant"
    assert existing_context.messages[3]["content"] == "El cambio de titularidad es sin costo administrativo."
    mock_context_repo.save.assert_awaited_once_with(existing_context)

