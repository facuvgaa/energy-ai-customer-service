export class VisionClientPort {
    async analyzeImage(sessionId, fileBuffer, filename, mimeType) {
        throw new Error("analyzeImage() must be implemented by subclass");
    }
}
