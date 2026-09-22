package com.example.demo.domain.repository;

import java.util.List;
import java.util.Optional;

import com.example.demo.domain.models.claims.Claim;

public interface ClaimRepository {
    Claim save(Claim claim);
    Optional<Claim> findById(Long id);
    Optional<Claim> findByClaimNumber(String claimNumber);
    List<Claim> findByServiceNumber(Long serviceNumber);
} 
