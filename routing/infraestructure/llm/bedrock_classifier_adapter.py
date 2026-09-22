import asyncio
import logging
import os
import boto3
from domain.models.message import WorkFlowTarget
from domain.ports.intent_classifier_port import IntentClassifierPort
from infraestructure.promps.promp_routing import SYSTEM_PROMPT
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

MODEL_ROUTING=os.getenv("MODEL_ROUTING", "anthropic.claude-3-haiku-20240307-v1:0")
REGION_NAME= os.getenv("REGION_NAME", "us-east-1")

class BedrockClassifierAdapter(IntentClassifierPort):
    def __init__(
        self,
        model_id: str =MODEL_ROUTING,
        region_name: str = REGION_NAME
    ):
        self._model_id = model_id
        self._client = boto3.client("bedrock_runtime", region_name= region_name) 

    def _call_bedrock(self, text:str)-> str:
        response = self._client.converse(
            modelId= self._model_id,
            messages=[
                {
                    "role":"user",
                    "content": [{"text": text}]
                }
            ],
            system=[{"text": SYSTEM_PROMPT}],
            inferenceConfig={
                "maxTokens": 10,
                "temperature": 0.0,
                "topP": 0.1
            }
        )
        return response["output"]["message"]["content"][0]["text"].strip().upper()

    async def classify (self, text:str):
        try:
            category = await asyncio.to_thread(self._call_bedrock, text)
            logger.info("Respuesta cruda de Bedrock: '%s'", category)
        except Exception as err:
            logger.error("Error al invocar Bedrock: %s", err, exc_info=True)
            return WorkFlowTarget.UNKNOWN

        if "RECLAMO" in category:
            return WorkFlowTarget.TECHNICAL_CLAIM
        elif "FACTURACION" in category:
            return WorkFlowTarget.BILLING
        elif "CONSULTA" in category:
            return WorkFlowTarget.GENERAL_QUERY
        
        logger.warning("Intención no reconocida en Bedrock: '%s' -> asignando UNKNOWN", category)
        return WorkFlowTarget.UNKNOWN