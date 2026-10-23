import { Kafka } from "kafkajs";
import { EventPublisherPort } from "../../domain/ports/event-publisher.port.js";

export class KafkaProducerAdapter extends EventPublisherPort {
    constructor(brokers = [process.env.KAFKA_BOOTSTRAP_SERVERS || "localhost:9092"]) {
        super();
        const kafka = new Kafka({
            clientId: "api-gateway-producer",
            brokers,
        });
        this.producer = kafka.producer();
    }

    async start() {
        await this.producer.connect();
        console.log("[KafkaProducer] Conectado a Kafka");
    }

    async stop() {
        await this.producer.disconnect();
    }

    async publish(topic, messagePayload) {
        await this.producer.send({
            topic,
            messages: [
                {
                    key: String(messagePayload.session_id),
                    value: JSON.stringify(messagePayload),
                },
            ],
        });
        console.log(`[KafkaProducer] Mensaje publicado en '${topic}' (session=${messagePayload.session_id})`);
    }
}

