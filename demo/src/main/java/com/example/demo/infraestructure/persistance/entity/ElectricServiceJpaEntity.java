package com.example.demo.infraestructure.persistance.entity;


import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import com.example.demo.domain.models.service.ServiceStatus;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "electric_services")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ElectricServiceJpaEntity {

    @Id
    @Column(name = "service_number")
    private Long serviceNumber;

    @Column(name = "client_id")
    private Long clientId;

    @Column(name = "address", nullable = false, length = 200)
    private String address;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 20)
    private ServiceStatus status;

    @Column(name = "cutoff_date")
    private LocalDate cutoffDate;

    @OneToMany(mappedBy = "electricService", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<EnergyBillJpaEntity> bills = new ArrayList<>();
    
    public void addBill(EnergyBillJpaEntity bill) {
        bills.add(bill);
        bill.setElectricService(this);
    }
}