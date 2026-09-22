package com.example.demo.infraestructure.rest.dto;

public record CreateClientRequest(
    String fullName,
    String email
) {}
