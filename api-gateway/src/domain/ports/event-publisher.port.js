export class EventPublisherPort {
    async publish(topic, messagePayload) {
        throw new Error("publish() must be implemented by subclass");
    }
}