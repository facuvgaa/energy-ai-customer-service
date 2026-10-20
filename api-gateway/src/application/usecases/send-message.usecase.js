export class SendMessageUseCase {
    constructor({ routeCache, visionClient, eventPublisher }) {
        this.routeCache = routeCache;
        this.visionClient = visionClient;
        this.eventPublisher = eventPublisher;
    }

    async execute(command) {
        let extractedDocument = null;

        if (command.fileBuffer) {
            extractedDocument = await this.visionClient.analyzeImage(
                command.sessionId,
                command.fileBuffer,
                command.filename,
                command.mimeType
            );
        }

        let targetTopic = await this.routeCache.getRoute(command.sessionId);

        if (!targetTopic && extractedDocument) {
            const docType = extractedDocument.document_type;
            if (docType === "INVOICE" || docType === "PAYMENT_RECEIPT") {
                targetTopic = "chat.workflow.billing";
                await this.routeCache.setRoute(command.sessionId, targetTopic);
            } else if (docType === "TECHNICAL_DAMAGE") {
                targetTopic = "chat.workflow.technical";
                await this.routeCache.setRoute(command.sessionId, targetTopic);
            }
        }

        if (!targetTopic) {
            targetTopic = "chat.incoming.unclassified";
        }

        const payload = {
            session_id: command.sessionId,
            user_id: command.userId,
            service_numbers: command.serviceNumbers,
            content: command.content,
            is_authenticated: true,
            extracted_document: extractedDocument,
            timestamp: new Date().toISOString(),
        };

        await this.eventPublisher.publish(targetTopic, payload);

        return {
            routedTo: targetTopic,
            extractedDocument,
        };
    }
}