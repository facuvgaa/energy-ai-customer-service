package com.example.demo.domain.repository;

import java.util.Optional;

import com.example.demo.domain.models.service.ElectricService;

public interface ElectricServiceRepository {
    ElectricService save(ElectricService service);
    Optional<ElectricService> findByServiceNumber(Long serviceNumber);
}
