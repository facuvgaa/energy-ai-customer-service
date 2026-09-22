package com.example.demo.infraestructure.rest.dto;

import java.time.LocalDate;

import com.example.demo.domain.models.claims.Claim;
import com.example.demo.domain.models.claims.ClaimStatus;
import com.example.demo.domain.models.claims.ClaimType;

public record ClaimResponse(
    Long id,
    String claimNumber,
    Long serviceNumber,
    String description,
    ClaimType type,
    ClaimStatus status,
    LocalDate date
) {
    public static ClaimResponse fromDomain(Claim claim) {
        return new ClaimResponse(
            claim.getId(),
            claim.getClaimNumber(),
            claim.getServiceNumber(),
            claim.getDescription(),
            claim.getType(),
            claim.getStatus(),
            claim.getDate()
        );
    }
}