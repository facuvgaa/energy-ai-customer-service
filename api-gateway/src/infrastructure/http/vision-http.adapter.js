import { VisionClientPort } from "../../domain/ports/vision-client.port.js";

export class VisionHttpAdapter extends VisionClientPort {
    constructor(visionBaseUrl = process.env.VISION_SERVICE_URL || "http://localhost:8001") {
        super();
        this.visionBaseUrl = visionBaseUrl;
    }

    async analyzeImage(sessionId, fileBuffer, filename, mimeType = "image/jpeg") {
        try {
            const formData = new FormData();
            formData.append("session_id", sessionId);

            const blob = new Blob([fileBuffer], { type: mimeType });
            formData.append("file", blob, filename || `doc_${sessionId}.jpg`);

            const response = await fetch(`${this.visionBaseUrl}/vision/analyze`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                console.error(`[VisionHttpAdapter] Error en Vision Service (${response.status}): ${response.statusText}`);
                return null;
            }

            return await response.json();
        } catch (err) {
            console.error(`[VisionHttpAdapter] Vision Service offline en ${this.visionBaseUrl}:`, err.message);
            return null;
        }
    }
}