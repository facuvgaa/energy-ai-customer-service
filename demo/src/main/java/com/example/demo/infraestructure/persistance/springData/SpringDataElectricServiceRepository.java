package com.example.demo.infraestructure.persistance.springData;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.demo.infraestructure.persistance.entity.ElectricServiceJpaEntity;

public interface SpringDataElectricServiceRepository extends JpaRepository<ElectricServiceJpaEntity, Long> {

    
}
