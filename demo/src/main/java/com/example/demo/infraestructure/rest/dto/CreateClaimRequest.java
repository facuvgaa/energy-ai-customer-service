package com.example.demo.infraestructure.rest.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import com.example.demo.domain.models.claims.ClaimType;

public record CreateClaimRequest(
    @NotNull(message = "El número de suministro es obligatorio")
    Long serviceNumber,

    @NotBlank(message = "La descripción no puede estar vacía")
    @Size(min = 80, message = "La descripción debe tener al menos 80 caracteres")
    String description,

    @NotNull(message = "El tipo de reclamo es obligatorio")
    ClaimType type
) {}