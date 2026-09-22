package com.example.demo.application.client.query;

public record GetClientByEmailQuery(String email) {
    public GetClientByEmailQuery {
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("El email de búsqueda no puede estar vacío");
        }
        email = email.trim().toLowerCase();
    }
}
