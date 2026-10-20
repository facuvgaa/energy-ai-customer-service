export class UserRepositoryPort{
    async findByEmail(email){
        throw new Error("findByEmail() must be implemented by subclass")
    }

    async save(userModel){
        throw new Error("save() must be implemented by subclass")
    }
}