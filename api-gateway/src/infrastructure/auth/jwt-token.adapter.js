import jwt from "jsonwebtoken";
import {TokenProviderPort} from "../../domain/ports/token-provider.port";


const DEFAULT_SECRET = process.env.JWT_SECRET || "electric-service-super-secret-key";


export class JwTokenAdapter extends TokenProviderPort{
    constructor(secret = DEFAULT_SECRET, expiresIn = "24h"){
        super();
        this.secret = secret;
        this.expiresIn = expiresIn;
    }

    generateToken(payload){
        return jwt.sign(payload, this.secret, {expiresIn: this.expiresIn});
    }

    verifyToken(token){
        return jwt.verify(token, this.secret);
    }
}