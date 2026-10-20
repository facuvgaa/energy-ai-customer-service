export class LoginUserCommand {
    constructor({ email, password }) {
        this.email = email;
        this.password = password;
        Object.freeze(this);
    }
}