package com.example.demo.domain.models.service;

import java.math.BigDecimal;

public record ConsumptionDetail(
    BigDecimal activeCurrentReading,
    BigDecimal activePreviousReading,
    BigDecimal activeConsumptionKwh,

    BigDecimal reactiveCurrentReading,
    BigDecimal reactivePreviousReading,

    BigDecimal cosPhi
) {
    public ConsumptionDetail {
        if (activeCurrentReading == null || activePreviousReading == null) {
            throw new IllegalArgumentException("Las lecturas activa actual y anterior son obligatorias");
        }
        if (activeCurrentReading.compareTo(activePreviousReading) < 0) {
            throw new IllegalArgumentException("La lectura actual no puede ser menor a la lectura anterior");
        }
        if (activeConsumptionKwh == null) {
            activeConsumptionKwh = activeCurrentReading.subtract(activePreviousReading);
        }
    }
}
