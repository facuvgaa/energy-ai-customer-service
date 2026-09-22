package com.example.demo.application.claim.usecase;

import java.util.NoSuchElementException;

import org.springframework.stereotype.Service;

import com.example.demo.application.claim.query.GetClaimByNumberQuery;
import com.example.demo.domain.models.claims.Claim;
import com.example.demo.domain.repository.ClaimRepository;

import lombok.RequiredArgsConstructor;

@Service 
@RequiredArgsConstructor 
public class GetClaimByNumberUseCase {

    private final ClaimRepository claimRepository;

    public Claim execute(GetClaimByNumberQuery query) {
        if (query == null || query.claimNumber() == null || query.claimNumber().isBlank()) {
            throw new IllegalArgumentException("The claim number cannot be null or blank");
        }

        return claimRepository.findByClaimNumber(query.claimNumber())
            .orElseThrow(() -> new NoSuchElementException("Claim not found: " + query.claimNumber()));
    }
}
