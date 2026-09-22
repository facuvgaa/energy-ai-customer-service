package com.example.demo.domain.models.claims;

import java.time.LocalDate;

import lombok.Getter;

@Getter 
public class Claim {
    private final Long id;
    private final String description;
    private final LocalDate date;
    private ClaimType type;
    private final Long serviceNumber;
    private final  String claimNumber;
    private  ClaimStatus status;


    public Claim(Long id, String description, LocalDate date, ClaimType type, Long serviceNumber, String claimNumber, ClaimStatus status) {
        if (description == null || description.trim().length() < 80) {
            throw new IllegalArgumentException("The description cannot be empty or have fewer than 80 characters");
        }
        if (type == null) {
            throw new IllegalArgumentException("The claim type is required");
        }
        if (serviceNumber == null || serviceNumber <= 0) {
            throw new IllegalArgumentException("A valid service number is required to register a claim");
        }

        this.id = id;
        this.description = description.trim();
        this.date = (date != null) ? date : LocalDate.now();
        this.type = type;
        this.serviceNumber = serviceNumber;
        this.claimNumber = claimNumber;
        this.status = (status != null) ? status : ClaimStatus.OPEN;
    }

    public void resolve() {
        if (this.status == ClaimStatus.RESOLVED) {
            throw new IllegalStateException("The claim is already resolved");
        }
        this.status = ClaimStatus.RESOLVED;
    }
}
