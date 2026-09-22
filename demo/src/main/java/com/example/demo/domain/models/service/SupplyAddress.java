package com.example.demo.domain.models.service;

public record SupplyAddress(String value) {
    public SupplyAddress {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("La dirección de suministro no puede estar vacía");
        }
        value = value.trim();
    }
}