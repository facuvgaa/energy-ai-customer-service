import { Server } from "socket.io";
import { SendMessageCommand } from "../../application/commands/send-message.command.js";

export class SocketGateway {
    constructor({ httpServer, tokenProvider, sendMessageUseCase }) {
        this.tokenProvider = tokenProvider;
        this.sendMessageUseCase = sendMessageUseCase;

        this.io = new Server(httpServer, {
            cors: { origin: "*" },
            maxHttpBufferSize: 10 * 1024 * 1024, // 10 MB para fotos de facturas
        });

        this._setupMiddleware();
        this._setupHandlers();
    }

    _setupMiddleware() {
        // Verifica el Token JWT antes de permitir que alguien abra el WebSocket
        this.io.use((socket, next) => {
            try {
                const token = socket.handshake.auth?.token;
                if (!token) {
                    return next(new Error("Token JWT requerido"));
                }
                const decoded = this.tokenProvider.verifyToken(token);
                socket.user = decoded;
                next();
            } catch (err) {
                next(new Error("Token JWT inválido o expirado"));
            }
        });
    }

    _setupHandlers() {
        this.io.on("connection", (socket) => {
            const sessionId = socket.handshake.auth?.sessionId || `sess_${socket.user.userId}`;
            socket.join(sessionId);
            console.log(`[SocketGateway] Usuario ${socket.user.email} conectado en sala '${sessionId}'`);

            socket.on("user_message", async (payload, callback) => {
                try {
                    const fileBuffer = payload.fileBase64
                        ? Buffer.from(payload.fileBase64, "base64")
                        : null;

                    const command = new SendMessageCommand({
                        sessionId,
                        userId: socket.user.userId,
                        serviceNumbers: socket.user.serviceNumbers || [],
                        content: payload.content || "",
                        fileBuffer,
                        filename: payload.filename || null,
                        mimeType: payload.mimeType || "image/jpeg",
                    });

                    const result = await this.sendMessageUseCase.execute(command);
                    if (callback) callback({ ok: true, ...result });
                } catch (err) {
                    console.error("[SocketGateway] Error enviando mensaje:", err);
                    if (callback) callback({ ok: false, error: err.message });
                }
            });
        });
    }

    emitBotResponse(sessionId, responseData) {
        this.io.to(sessionId).emit("bot_response", responseData);
    }

    emitRouteUpdate(sessionId, targetTopic) {
        this.io.to(sessionId).emit("route_updated", { sessionId, targetTopic });
    }
}

