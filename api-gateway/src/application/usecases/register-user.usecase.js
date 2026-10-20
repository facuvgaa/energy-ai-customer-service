import bcrypt from "bcryptjs";
import crypto from "crypto";
import { UserModel } from "../../domain/models/user.model.js";

export class RegisterUserUseCase {
    constructor({ userRepository, tokenProvider }) {
        this.userRepository = userRepository;
        this.tokenProvider = tokenProvider;
    }

    async execute(command) {
        const existingUser = await this.userRepository.findByEmail(command.email);
        if (existingUser) {
            throw new Error("El email ya está registrado");
        }

        const passwordHash = await bcrypt.hash(command.password, 10);

        const newUser = new UserModel({
            id: crypto.randomUUID(),
            email: command.email,
            passwordHash: passwordHash,
            fullName: command.fullName,
            serviceNumbers: command.serviceNumbers,
        });

        const savedUser = await this.userRepository.save(newUser);

        const token = this.tokenProvider.generateToken({
            userId: savedUser.id,
            email: savedUser.email,
            serviceNumbers: savedUser.serviceNumbers,
        });

        return {
            user: savedUser.toPublicProfile(),
            token: token,
        };
    }
}