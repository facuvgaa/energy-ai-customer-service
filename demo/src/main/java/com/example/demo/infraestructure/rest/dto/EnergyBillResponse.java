package com.example.demo.infraestructure.rest.dto;

import java.math.BigDecimal;
import java.time.LocalDate;

public record EnergyBillResponse(
    String billNumber,
    BigDecimal amount,
    String period,
    LocalDate dueDate,
    String status,
    ConsumptionDetailResponse consumptionDetail
) {}