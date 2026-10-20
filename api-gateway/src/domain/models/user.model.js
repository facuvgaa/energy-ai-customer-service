export class UserModel {
    constructor({
        id,
        email,
        passwordHash,
        fullName,
        serviceNumbers = [],
        createdAt = new Date(),
    }) {
        this.id = id;
        this.email = email;
        this.passwordHash = passwordHash;
        this.fullName = fullName;
        this.serviceNumbers = serviceNumbers;
        this.createdAt = createdAt;
    }

    toPublicProfile() {
        return {
            id: this.id,
            email: this.email,
            fullName: this.fullName,
            serviceNumbers: this.serviceNumbers,
        };
    }
}

