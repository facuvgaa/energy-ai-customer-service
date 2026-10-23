import { Kafka } from "kafkajs";

export class KafkaConsumerAdapter {
    constructor({
        routeCache,
        socketGateway,
        brokers = [process.env.KAFKA_BOOTSTRAP_SERVERS || "localhost:9092"],
        groupId = "api-gateway-consumer-group",
    }) {
        this.routeCache = routeCache;
        this.socketGateway = socketGateway;

        const kafka = new Kafka({
            clientId: "api-gateway-consumer",
            brokers,
        });
        this.consumer = kafka.consumer({ groupId });
    }

    async start() {
        await this.consumer.connect();
        await this.consumer.subscribe({
            topics: ["chat.session.routed", "chat.outgoing.response"],
            fromBeginning: false,
        });

        await this.consumer.run({
            eachMessage: async ({ topic, message }) => {
                if (!message.value) return;
                const data = JSON.parse(message.value.toString("utf-8"));

                if (topic === "chat.session.routed") {
                    // Routing nos avisa a qué tópico quedó fijada esta sesión
                    await this.routeCache.setRoute(data.session_id, data.target_topic);
                    this.socketGateway.emitRouteUpdate(data.session_id, data.target_topic);
                } else if (topic === "chat.outgoing.response") {
                    // Un microservicio (ej: Billing) respondió al cliente
                    this.socketGateway.emitBotResponse(data.session_id, data);
                }
            },
        });
        console.log("[KafkaConsumer] Escuchando 'chat.session.routed' y 'chat.outgoing.response'");
    }

    async stop() {
        await this.consumer.disconnect();
    }
}

