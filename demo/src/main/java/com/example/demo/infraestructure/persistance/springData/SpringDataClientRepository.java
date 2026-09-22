package com.example.demo.infraestructure.persistance.springData;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.demo.infraestructure.persistance.entity.ClientJpaEntity;

public  interface SpringDataClientRepository extends JpaRepository<ClientJpaEntity, Long> {
    Optional <ClientJpaEntity> findByEmail(String email);
    
}