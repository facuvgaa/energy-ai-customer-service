package com.example.demo.infraestructure.rest.dto;

import java.math.BigDecimal;

public record ConsumptionDetailResponse(
    BigDecimal activeCurrentReading,
    BigDecimal activePreviousReading,
    BigDecimal activeConsumptionKwh,
    BigDecimal reactiveCurrentReading,
    BigDecimal reactivePreviousReading,
    BigDecimal cosPhi
) {}
