package com.example.demo.application.claim.usecase;

import java.util.List;

import org.springframework.stereotype.Service;

import com.example.demo.application.claim.query.GetClaimsByServiceNumberQuery;
import com.example.demo.domain.models.claims.Claim;
import com.example.demo.domain.repository.ClaimRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class GetClaimsByServiceNumberUseCase {

    private final ClaimRepository claimRepository;

    public List<Claim> execute(GetClaimsByServiceNumberQuery query) {
        return claimRepository.findByServiceNumber(query.serviceNumber());
    }
}
