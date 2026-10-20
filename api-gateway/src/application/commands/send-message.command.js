export class SendMessageCommand {
    constructor({
        sessionId,
        userId,
        serviceNumbers = [],
        content,
        fileBuffer = null,
        filename = null,
        mimeType = null,
    }) {
        this.sessionId = sessionId;
        this.userId = userId;
        this.serviceNumbers = serviceNumbers;
        this.content = content;
        this.fileBuffer = fileBuffer;
        this.filename = filename;
        this.mimeType = mimeType;
        Object.freeze(this);
    }
}