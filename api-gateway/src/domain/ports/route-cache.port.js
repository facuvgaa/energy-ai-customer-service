export class RouteCachePort {
    async getRoute(sessionId) {
        throw new Error("getRoute() must be implemented by subclass");
    }

    async setRoute(sessionId, targetTopic) {
        throw new Error("setRoute() must be implemented by subclass");
    }
}