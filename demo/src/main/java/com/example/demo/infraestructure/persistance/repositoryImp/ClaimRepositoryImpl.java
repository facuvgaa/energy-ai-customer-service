package com.example.demo.infraestructure.persistance.repositoryImp;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.stereotype.Repository;

import com.example.demo.domain.models.claims.Claim;
import com.example.demo.domain.repository.ClaimRepository;
import com.example.demo.infraestructure.persistance.entity.ClaimJpaEntity;
import com.example.demo.infraestructure.persistance.springData.SpringDataClaimRepository;

import lombok.RequiredArgsConstructor;

@Repository
@RequiredArgsConstructor
public class ClaimRepositoryImpl implements ClaimRepository {

    private final SpringDataClaimRepository springDataClaimRepository;

    @Override
    public Claim save(Claim claim) {
        ClaimJpaEntity entity = new ClaimJpaEntity(
            claim.getId(),
            claim.getDescription(),
            claim.getDate(),
            claim.getServiceNumber(),
            claim.getClaimNumber(),
            claim.getType(),
            claim.getStatus()
        );

        ClaimJpaEntity savedEntity = springDataClaimRepository.save(entity);

        return toDomain(savedEntity);
    }

    @Override
    public Optional<Claim> findById(Long id) {
        return springDataClaimRepository.findById(id)
            .map(this::toDomain);
    }

    @Override
    public Optional<Claim> findByClaimNumber(String claimNumber) {
        return springDataClaimRepository.findByClaimNumber(claimNumber)
            .map(this::toDomain);
    }

    @Override
    public List<Claim> findByServiceNumber(Long serviceNumber) {
        return springDataClaimRepository.findByServiceNumber(serviceNumber)
            .stream()
            .map(this::toDomain)
            .collect(Collectors.toList());
    }

    private Claim toDomain(ClaimJpaEntity entity) {
        return new Claim(
            entity.getId(),
            entity.getDescription(),
            entity.getDate(),
            entity.getType(),
            entity.getServiceNumber(),
            entity.getClaimNumber(),
            entity.getStatus()
        );
    }
}