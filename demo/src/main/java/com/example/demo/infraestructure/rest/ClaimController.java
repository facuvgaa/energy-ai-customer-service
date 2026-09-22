package com.example.demo.infraestructure.rest;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.application.claim.command.CreateClaimCommand;
import com.example.demo.application.claim.query.GetClaimByNumberQuery;
import com.example.demo.application.claim.query.GetClaimsByServiceNumberQuery;
import com.example.demo.application.claim.usecase.CreateClaimUseCase;
import com.example.demo.application.claim.usecase.GetClaimByNumberUseCase;
import com.example.demo.application.claim.usecase.GetClaimsByServiceNumberUseCase;
import com.example.demo.domain.models.claims.Claim;
import com.example.demo.infraestructure.rest.dto.ClaimResponse;
import com.example.demo.infraestructure.rest.dto.CreateClaimRequest;

import lombok.AllArgsConstructor;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;


@RestController  
@RequestMapping("/api/claim")
@AllArgsConstructor
public class ClaimController {
    private final CreateClaimUseCase createClaimUseCase;
    private final GetClaimByNumberUseCase getClaimByNumberUseCase;
    private final GetClaimsByServiceNumberUseCase getClaimsByServiceNumberUseCase;


    @PostMapping
    public ResponseEntity<String> createClaim(@RequestBody CreateClaimRequest request) {
        CreateClaimCommand command = new CreateClaimCommand
        (request.serviceNumber(), 
        request.description(), 
        request.type()
        );
        
        String claimNumber = createClaimUseCase.execute(command);
        return ResponseEntity.status(HttpStatus.CREATED).body(claimNumber);
    }

    @GetMapping("/{claimNumber}")
    public ResponseEntity<ClaimResponse> getByClaimNumber(@PathVariable String claimNumber) {
        GetClaimByNumberQuery query = new GetClaimByNumberQuery(claimNumber);
        Claim claim = getClaimByNumberUseCase.execute(query);
        return ResponseEntity.ok(ClaimResponse.fromDomain(claim));
    }

    @GetMapping("/service/{serviceNumber}")
    public ResponseEntity<List<ClaimResponse>> getByServiceNumber(@PathVariable Long serviceNumber) {
        GetClaimsByServiceNumberQuery query = new GetClaimsByServiceNumberQuery(serviceNumber);
        List<ClaimResponse> claims = getClaimsByServiceNumberUseCase.execute(query)
            .stream()
            .map(ClaimResponse::fromDomain)
            .toList();

        return ResponseEntity.ok(claims);
    }
    
}
