package com.example.demo.infraestructure.persistance.springData;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.demo.infraestructure.persistance.entity.ClaimJpaEntity;

public interface SpringDataClaimRepository extends JpaRepository<ClaimJpaEntity, Long> {

    Optional<ClaimJpaEntity> findByClaimNumber(String claimNumber);

    List<ClaimJpaEntity> findByServiceNumber(Long serviceNumber);
}
