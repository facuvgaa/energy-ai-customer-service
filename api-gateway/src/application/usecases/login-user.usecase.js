import bcrypt from "bcryptjs";


export class LoginUserCase{
    constructor({userRepository, tokenProvider}){
        this.userRepository = userRepository;
        this.tokenProvider = tokenProvider;
    }

    async execute(command){
        const user = await this.userRepository.findByEmail(command.email);
        if(!user){
            throw new Error("ivalid credencials")
        }

        const isPasswordValid = await bcrypt.compare(command.password, user.passwordHash);
        if (!isPasswordValid) {
            throw new Error("Credenciales inválidas");
        }
        const token = this.tokenProvider.generateToken({
            userId: user.id,
            email: user.email,
            serviceNumbers: user.serviceNumbers,
        });
        return {
            user: user.toPublicProfile(),
            token: token,
        };
    }
}