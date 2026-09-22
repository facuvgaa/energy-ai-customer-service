package com.example.demo.infraestructure.persistance.entity;

import java.math.BigDecimal;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Embeddable
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ConsumptionDetailEmbeddable {

    @Column(name = "active_current_reading", precision = 10, scale = 3)
    private BigDecimal activeCurrentReading;

    @Column(name = "active_previous_reading", precision = 10, scale = 3)
    private BigDecimal activePreviousReading;

    @Column(name = "active_consumption_kwh", precision = 10, scale = 3)
    private BigDecimal activeConsumptionKwh;

    @Column(name = "reactive_current_reading", precision = 10, scale = 3)
    private BigDecimal reactiveCurrentReading;

    @Column(name = "reactive_previous_reading", precision = 10, scale = 3)
    private BigDecimal reactivePreviousReading;

    @Column(name = "cos_phi", precision = 4, scale = 2)
    private BigDecimal cosPhi;
}