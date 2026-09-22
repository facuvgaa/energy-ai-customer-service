package com.example.demo.application.claim.command;

import com.example.demo.domain.models.claims.ClaimType;

public record CreateClaimCommand(
    Long serviceNumber,
    String description,
    ClaimType type
) {}