import "dotenv/config";
import http from "http";
import path from "path";
import { fileURLToPath } from "url";
import express from "express";
import cors from "cors";

import { PostgresUserRepository } from "./infrastructure/db/postgres-user.repository.js";
import { JwtTokenAdapter } from "./infrastructure/auth/jwt-token.adapter.js";
import { RedisRouteAdapter } from "./infrastructure/cache/redis-route.adapter.js";
import { VisionHttpAdapter } from "./infrastructure/http/vision-http.adapter.js";
import { KafkaProducerAdapter } from "./infrastructure/kafka/kafka-producer.adapter.js";
import { KafkaConsumerAdapter } from "./infrastructure/kafka/kafka-consumer.adapter.js";
import { SocketGateway } from "./infrastructure/websocket/socket.gateway.js";

import { RegisterUserCommand } from "./application/commands/register-user.command.js";
import { LoginUserCommand } from "./application/commands/login-user.command.js";
import { RegisterUserUseCase } from "./application/usecases/register-user.usecase.js";
import { LoginUserUseCase } from "./application/usecases/login-user.usecase.js";
import { SendMessageUseCase } from "./application/usecases/send-message.usecase.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function bootstrap() {
    const app = express();
    app.use(cors());
    app.use(express.json());
    app.use(express.static(path.join(__dirname, "../public")));

    // 1. Inicializar Adaptadores de Infraestructura
    const userRepository = new PostgresUserRepository();
    await userRepository.initTable();

    const tokenProvider = new JwtTokenAdapter();
    const routeCache = new RedisRouteAdapter();
    const visionClient = new VisionHttpAdapter();
    const kafkaProducer = new KafkaProducerAdapter();
    await kafkaProducer.start();

    // 2. Inicializar Casos de Uso
    const registerUserUseCase = new RegisterUserUseCase({ userRepository, tokenProvider });
    const loginUserUseCase = new LoginUserUseCase({ userRepository, tokenProvider });
    const sendMessageUseCase = new SendMessageUseCase({
        routeCache,
        visionClient,
        eventPublisher: kafkaProducer,
    });

    // 3. Endpoints HTTP de Autenticación
    app.post("/auth/register", async (req, res) => {
        try {
            const command = new RegisterUserCommand({
                email: req.body.email,
                password: req.body.password,
                fullName: req.body.fullName,
                serviceNumbers: req.body.serviceNumbers || [],
            });
            const result = await registerUserUseCase.execute(command);
            res.status(201).json(result);
        } catch (err) {
            res.status(400).json({ error: err.message });
        }
    });

    app.post("/auth/login", async (req, res) => {
        try {
            const command = new LoginUserCommand({
                email: req.body.email,
                password: req.body.password,
            });
            const result = await loginUserUseCase.execute(command);
            res.json(result);
        } catch (err) {
            res.status(401).json({ error: err.message });
        }
    });

    // 4. Servidor HTTP + WebSockets + Kafka Consumer
    const httpServer = http.createServer(app);
    const socketGateway = new SocketGateway({
        httpServer,
        tokenProvider,
        sendMessageUseCase,
    });

    const kafkaConsumer = new KafkaConsumerAdapter({
        routeCache,
        socketGateway,
    });
    await kafkaConsumer.start();

    const PORT = process.env.PORT || 3000;
    httpServer.listen(PORT, () => {
        console.log(`[API Gateway] Corriendo en http://localhost:${PORT}`);
    });
}

bootstrap().catch((err) => {
    console.error("[API Gateway] Error fatal al iniciar:", err);
    process.exit(1);
});

