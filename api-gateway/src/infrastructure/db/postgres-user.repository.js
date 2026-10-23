import pg from "pg";
import { UserRepositoryPort } from "../../domain/ports/user-repository.port.js";
import { UserModel } from "../../domain/models/user.model.js";

const { Pool } = pg;

export class PostgresUserRepository extends UserRepositoryPort {
    constructor() {
        super();
        this.pool = new Pool({
            host: process.env.PG_HOST || "localhost",
            port: Number(process.env.PG_PORT || 5433),
            database: process.env.PG_DATABASE || "clientsdb",
            user: process.env.PG_USER || "client_user",
            password: process.env.PG_PASSWORD || "client_secret",
            max: 10,
        });
    }

    // Crea la tabla automáticamente al levantar el Gateway si no existe
    async initTable() {
        const query = `
            CREATE TABLE IF NOT EXISTS gateway_users (
                id UUID PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                service_numbers TEXT[] DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        `;
        await this.pool.query(query);
    }

    async findByEmail(email) {
        const result = await this.pool.query(
            "SELECT * FROM gateway_users WHERE email = $1",
            [email]
        );

        if (result.rows.length === 0) {
            return null;
        }

        const row = result.rows[0];
        return new UserModel({
            id: row.id,
            email: row.email,
            passwordHash: row.password_hash,
            fullName: row.full_name,
            serviceNumbers: row.service_numbers || [],
            createdAt: row.created_at,
        });
    }

    async save(userModel) {
        const query = `
            INSERT INTO gateway_users (id, email, password_hash, full_name, service_numbers, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *;
        `;
        const values = [
            userModel.id,
            userModel.email,
            userModel.passwordHash,
            userModel.fullName,
            userModel.serviceNumbers,
            userModel.createdAt,
        ];

        await this.pool.query(query, values);
        return userModel;
    }
}