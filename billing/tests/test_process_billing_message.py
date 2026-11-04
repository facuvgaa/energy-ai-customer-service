import pytest
from unittest.mock import AsyncMock

from application.command.process_billing_message_command import ProcessBillingMessageCommand
from application.usecase.process_billing_message_usecase import ProcessBillingMessageUsecase
from domain.models.billing_context_model import BillingContextModel
from domain.ports.billing_assistand_port import BillingAssistandPort
from domain.ports.billing_context_repository_port import BillingContextRepositoryPort


@pytest.mark.asyncio
async def test_process_billing_message_new_session():
    mock_repo = AsyncMock(spec=BillingContextRepositoryPort)
    mock_assistant = AsyncMock(spec=BillingAssistandPort)

    mock_repo.get_by_session_id.return_value = None

    async def fake_process_message(user_message, context):
        return "Tu saldo actual es de $15.420 con vencimiento el 10/11.", context

    mock_assistant.process_message.side_effect = fake_process_message

    use_case = ProcessBillingMessageUsecase(
        repository=mock_repo,
        assistant=mock_assistant,
    )

    command = ProcessBillingMessageCommand(
        session_id="billing-session-001",
        user_id="user-789",
        content="¿Cuánto debo de mi factura?",
        is_authenticated=True,
        service_numbers=["100200300"],
    )

    response = await use_case.execute(command)

    assert "Tu saldo actual es de $15.420" in response
    mock_repo.get_by_session_id.assert_awaited_once_with("billing-session-001")
    mock_assistant.process_message.assert_awaited_once()
    mock_repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_billing_message_existing_session():
    mock_repo = AsyncMock(spec=BillingContextRepositoryPort)
    mock_assistant = AsyncMock(spec=BillingAssistandPort)

    existing_context = BillingContextModel(
        session_id="billing-session-002",
        user_id="user-999",
        is_autenticated=True,
        service_numbers=["200300400"],
        messages=[
            {"role": "user", "content": "Hola"},
            {"role": "assistant", "content": "Hola, ¿en qué te puedo ayudar con tu facturación?"},
        ],
    )
    mock_repo.get_by_session_id.return_value = existing_context

    async def fake_process_message(user_message, context):
        return "Tu última factura fue abonada correctamente.", context

    mock_assistant.process_message.side_effect = fake_process_message

    use_case = ProcessBillingMessageUsecase(
        repository=mock_repo,
        assistant=mock_assistant,
    )

    command = ProcessBillingMessageCommand(
        session_id="billing-session-002",
        user_id="user-999",
        content="¿Se acreditó mi pago?",
    )

    response = await use_case.execute(command)

    assert response == "Tu última factura fue abonada correctamente."
    assert len(existing_context.messages) == 4
    assert existing_context.messages[2]["content"] == "¿Se acreditó mi pago?"
    assert existing_context.messages[3]["content"] == "Tu última factura fue abonada correctamente."
    mock_repo.save.assert_awaited_once_with(existing_context)


@pytest.mark.asyncio
async def test_process_billing_message_with_extracted_document():
    mock_repo = AsyncMock(spec=BillingContextRepositoryPort)
    mock_assistant = AsyncMock(spec=BillingAssistandPort)

    mock_repo.get_by_session_id.return_value = None

    captured_message = {}

    async def fake_process_message(user_message, context):
        captured_message["text"] = user_message
        return "Comprobante de pago procesado exitosamente por $5.000.", context

    mock_assistant.process_message.side_effect = fake_process_message

    use_case = ProcessBillingMessageUsecase(
        repository=mock_repo,
        assistant=mock_assistant,
    )

    command = ProcessBillingMessageCommand(
        session_id="billing-session-003",
        user_id="user-111",
        content="Acá te paso el comprobante que pagué hoy",
        extracted_document={
            "document_type": "PAYMENT_RECEIPT",
            "service_number": "100200300",
            "amount": 5000.0,
            "transaction_id": "TRX-987654",
            "image_url": "http://minio:9000/images/receipt.png",
        },
    )

    response = await use_case.execute(command)

    assert "procesado exitosamente por $5.000" in response
    assert "[Documento adjunto procesado por Vision" in captured_message["text"]
    assert "suministro=100200300" in captured_message["text"]
    assert "monto=5000.0" in captured_message["text"]
    mock_repo.save.assert_awaited_once()

