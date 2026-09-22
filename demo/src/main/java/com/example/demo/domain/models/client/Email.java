package com.example.demo.domain.models.client;

import java.util.regex.Pattern;

public record Email(String value){

    private static  final Pattern EMAIL_PATTERN = 
        Pattern.compile("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$");
    public Email {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("El email no puede estar vacío");
        }
        if (!EMAIL_PATTERN.matcher(value.trim()).matches()) {
            throw new IllegalArgumentException("Formato de email inválido: " + value);
        }
        value = value.trim().toLowerCase();
    }   
}