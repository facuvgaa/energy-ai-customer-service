import Redis from "ioredis"
import {RouteCachePort} from "../../domain/ports/route-cache.port"

export class RedisRouteAdapter extends RouteCachePort{
    constructor(redisUrl = process.env.REDIS_URL || "redis://localhost:6379", ttlSeconds = 3600)
    {
        super();
        this.client = new Redis(redisUrl)
        this.ttl = ttlSeconds;
    }
    async getRoute(sessionId) {
        return await this.client.get(`gateway:route:${sessionId}`);
    }
    async setRoute(sessionId, targetTopic) {
        await this.client.set(`gateway:route:${sessionId}`, targetTopic, "EX", this.ttl);
    }
}