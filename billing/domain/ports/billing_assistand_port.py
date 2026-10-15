from abc import ABC, abstractmethod
from domain.models.billing_context_model import  BillingContextModel

class BillingAssistandPort(ABC):
    @abstractmethod
    async def process_message(self, user_message: str, context: BillingContextModel)-> tuple[str, BillingContextModel]:
        """
        Procesa el mensaje del usuario utilizando el contexto actual de facturación.
        
        Retorna:
            - str: Mensaje de respuesta generado para el usuario.
            - BillingContext: Contexto actualizado (ej. si el usuario proporcionó 
              su número de suministro o se cargó su cuenta).
        """

        """

        Processes the user's message using the current billing context.

        Returns:

        - str: Response message generated for the user.

        - BillingContext: Updated context (e.g., if the user provided their supply number or their account was charged).

        """ 
        pass
