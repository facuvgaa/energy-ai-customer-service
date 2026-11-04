import pytest
from unittest.mock import AsyncMock

from application.command.claims_command import ClaimCommand
from application.usecase.process_claim_message_usecase import ProcessClaimMessageUsecase
from domain.models.claim_assistant_result_model import AssistantResultModel
from domain.models.claim_context_model import ClaimContextModel
from domain.models.claim_model import ClaimModel, ClaimCategory, ClaimPriority, ClaimStatus
from domain.ports.claim_assistant_port import ClaimAssistantPort
from domain.ports.claim_context_repository_port import ClaimContextRepositoryPort
from domain.ports.claim_repository_port import ClaimRepositoryPort


@pytest.mark.asyncio
async def test_process_claim_message_new_session():
    mock_claim_repo = AsyncMock(spec=ClaimRepositoryPort)
    mock_assistant = AsyncMock(spec=ClaimAssistantPort)
    mock_context_repo = AsyncMock(spec=ClaimContextRepositoryPort)

    mock_context_repo.get_by_session_id.return_value = None

    mock_assistant.process_message.return_value = AssistantResultModel(
        response_text="Peligro registrado. Cuadrilla en camino. Por favor manténgase a más de 10 metros.",
        create_claim=None,
    )

    use_case = ProcessClaimMessageUsecase(
        repository=mock_claim_repo,
        assistant=mock_assistant,
        context_repository=mock_context_repo,
    )

    command = ClaimCommand(
        session_id="claim-session-001",
        user_id="user-001",
        content="Se cayó un poste con cables chispeando en Av. Corrientes 1500",
        service_numbers=["123456"],
    )

    response = await use_case.execute(command)

    assert "manténgase a más de 10 metros" in response
    mock_context_repo.get_by_session_id.assert_awaited_once_with("claim-session-001")
    mock_assistant.process_message.assert_awaited_once()
    mock_context_repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_claim_message_with_vision_document():
    mock_claim_repo = AsyncMock(spec=ClaimRepositoryPort)
    mock_assistant = AsyncMock(spec=ClaimAssistantPort)
    mock_context_repo = AsyncMock(spec=ClaimContextRepositoryPort)

    mock_context_repo.get_by_session_id.return_value = None

    captured_message = {}

    async def fake_assistant_process(user_message, context):
        captured_message["text"] = user_message
        return AssistantResultModel(
            response_text="Hemos identificado el transformador averiado en la foto.",
            create_claim=None,
        )

    mock_assistant.process_message.side_effect = fake_assistant_process

    use_case = ProcessClaimMessageUsecase(
        repository=mock_claim_repo,
        assistant=mock_assistant,
        context_repository=mock_context_repo,
    )

    command = ClaimCommand(
        session_id="claim-session-002",
        user_id="user-002",
        content="Miren la foto de cómo quedó el transformador",
        extracted_document={
            "document_type": "TECHNICAL_DAMAGE",
            "service_number": "987654",
            "description": "Transformador echando humo negro y cables cortados en vereda",
            "image_url": "http://minio:9000/images/transformer_damage.jpg",
        },
    )

    response = await use_case.execute(command)

    assert "transformador averiado" in response
    assert "[Foto adjunta analizada por Vision AI" in captured_message["text"]
    assert "Transformador echando humo negro" in captured_message["text"]
    mock_context_repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_claim_message_creates_claim_in_repo():
    mock_claim_repo = AsyncMock(spec=ClaimRepositoryPort)
    mock_assistant = AsyncMock(spec=ClaimAssistantPort)
    mock_context_repo = AsyncMock(spec=ClaimContextRepositoryPort)

    mock_context_repo.get_by_session_id.return_value = None

    created_claim = ClaimModel(
        claim_id="CLM-7788",
        service_number="123456",
        category=ClaimCategory.INFRASTRUCTURE_DANGER,
        priority=ClaimPriority.URGENT,
        status=ClaimStatus.IN_PROGRESS,
        description="Poste caído con peligro en la vía pública",
    )

    mock_assistant.process_message.return_value = AssistantResultModel(
        response_text="Reclamo CLM-7788 generado con éxito.",
        create_claim=created_claim,
    )

    use_case = ProcessClaimMessageUsecase(
        repository=mock_claim_repo,
        assistant=mock_assistant,
        context_repository=mock_context_repo,
    )

    command = ClaimCommand(
        session_id="claim-session-003",
        user_id="user-003",
        content="Por favor generen el reclamo urgente",
    )

    response = await use_case.execute(command)

    assert "CLM-7788" in response
    mock_claim_repo.save.assert_awaited_once_with(created_claim)
    mock_context_repo.save.assert_awaited_once()

