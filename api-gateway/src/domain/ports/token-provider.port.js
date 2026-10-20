export class TokenProviderPort{
    generateToken(payload){
        throw new Error("generateToken() must be implemented by subclass")
    }

    verifyToken(token){
        throw new Error("verify() must be implemented by subclass")
    }
}