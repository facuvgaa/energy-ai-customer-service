export class RegisterUserCommand {
    constructor({ email, password, fullName, serviceNumbers = [] }) {
        this.email = email;
        this.password = password;
        this.fullName = fullName;
        this.serviceNumbers = serviceNumbers;
        Object.freeze(this);
    }
}