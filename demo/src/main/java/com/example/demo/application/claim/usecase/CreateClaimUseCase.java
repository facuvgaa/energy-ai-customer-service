package com.example.demo.application.claim.usecase;

import java.util.UUID;

import org.springframework.stereotype.Service;

import com.example.demo.application.claim.command.CreateClaimCommand;
import com.example.demo.domain.models.claims.Claim;
import com.example.demo.domain.repository.ClaimRepository;
import com.example.demo.domain.repository.ElectricServiceRepository;

import lombok.RequiredArgsConstructor;

@Service 
@RequiredArgsConstructor 
public class CreateClaimUseCase {

    private final ClaimRepository claimRepository;
    private final ElectricServiceRepository electricServiceRepository;
    
    public String execute(CreateClaimCommand command) {

        electricServiceRepository.findByServiceNumber(command.serviceNumber())
            .orElseThrow(() -> new IllegalArgumentException("Electric service not found: " + command.serviceNumber()));

        String claimNumber = "CLM-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();

        Claim claim = new Claim(
            null,
            command.description(),
            null,
            command.type(),
            command.serviceNumber(),
            claimNumber,
            null
        );

        claimRepository.save(claim);

        return claimNumber;
    }
}