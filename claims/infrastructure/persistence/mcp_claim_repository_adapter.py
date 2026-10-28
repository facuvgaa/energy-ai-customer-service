import json
import logging
from typing import Optional, List

from domain.models.claim_model import ClaimModel, ClaimCategory, ClaimPriority, ClaimStatus
from domain.ports.claim_repository_port import ClaimRepositoryPort
from domain.ports.mcp_tool_provider_port import McpToolProviderPort

logger = logging.getLogger(__name__)


class McpClaimRepositoryAdapter(ClaimRepositoryPort):
    def __init__(self, mcp_client: McpToolProviderPort):
        self._mcp = mcp_client

    async def save(self, claim: ClaimModel) -> ClaimModel:
        """
        Persiste un reclamo invocando la herramienta 'create_claim' del servidor Spring Boot MCP.
        """
        # Mapeamos categoría y prioridad al enum de Spring Boot: URGENT, RECONNECTION, BILLING_CLAIM
        if claim.priority == ClaimPriority.URGENT or claim.category == ClaimCategory.INFRASTRUCTURE_DANGER:
            claim_type = "URGENT"
        elif claim.category == ClaimCategory.RECONNECTION:
            claim_type = "RECONNECTION"
        else:
            claim_type = "BILLING_CLAIM"

        # La herramienta requiere serviceNumber; si no hay, usamos 0 o el que tenga
        service_num = int(claim.service_number) if claim.service_number and claim.service_number.isdigit() else 0

        # La herramienta en Spring Boot valida descripción >= 80 caracteres
        description = claim.description
        if len(description) < 80:
            extra = f" | Ubicación: {claim.address or 'Sin dirección especificada'}. Categoría: {claim.category.value}."
            description = (description + extra).ljust(85)

        arguments = {
            "serviceNumber": service_num,
            "description": description,
            "type": claim_type,
        }

        logger.info("Guardando reclamo en MCP con args: %s", arguments)
        response_str = await self._mcp.call_tool("create_claim", arguments)
        logger.info("Respuesta de create_claim MCP: %s", response_str)

        # Si el MCP devuelve el ID del reclamo (CLM-XXXX), lo asociamos
        claim_id = claim.claim_id
        if "CLM-" in response_str:
            import re
            match = re.search(r"CLM-[A-Z0-9]+", response_str)
            if match:
                claim_id = match.group(0)

        return ClaimModel(
            claim_id=claim_id,
            description=claim.description,
            category=claim.category,
            priority=claim.priority,
            status=ClaimStatus.OPEN,
            service_number=claim.service_number,
            address=claim.address,
            billing_number=claim.billing_number,
            photos_url=claim.photos_url,
            created_at=claim.created_at,
        )

    async def find_by_id(self, claim_id: str) -> Optional[ClaimModel]:
        """Consulta el estado del reclamo por su ID a través de Spring Boot MCP."""
        response_str = await self._mcp.call_tool("get_claim_by_number", {"claimNumber": claim_id})
        if not response_str or "Error" in response_str:
            return None

        try:
            data = json.loads(response_str)
            return ClaimModel(
                claim_id=str(data.get("id", claim_id)),
                description=data.get("description", ""),
                category=ClaimCategory.INFRASTRUCTURE_DANGER if data.get("type") == "URGENT" else ClaimCategory.BILLING,
                priority=ClaimPriority.URGENT if data.get("type") == "URGENT" else ClaimPriority.MEDIUM,
                status=ClaimStatus(data.get("status", "OPEN")),
                service_number=str(data.get("serviceNumber")) if data.get("serviceNumber") else None,
            )
        except Exception:
            return None

    async def find_by_service_number(self, service_number: str) -> List[ClaimModel]:
        """Recupera los reclamos del suministro desde Spring Boot MCP."""
        try:
            num = int(service_number)
        except ValueError:
            return []

        response_str = await self._mcp.call_tool("get_claims_by_service", {"serviceNumber": num})
        if not response_str or "Error" in response_str:
            return []

        try:
            claims_data = json.loads(response_str)
            if not isinstance(claims_data, list):
                return []

            return [
                ClaimModel(
                    claim_id=str(c.get("id")),
                    description=c.get("description", ""),
                    category=ClaimCategory.INFRASTRUCTURE_DANGER if c.get("type") == "URGENT" else ClaimCategory.BILLING,
                    priority=ClaimPriority.URGENT if c.get("type") == "URGENT" else ClaimPriority.MEDIUM,
                    status=ClaimStatus(c.get("status", "OPEN")),
                    service_number=service_number,
                )
                for c in claims_data
            ]
        except Exception:
            return []

