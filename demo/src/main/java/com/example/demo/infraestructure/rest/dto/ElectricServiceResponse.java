package com.example.demo.infraestructure.rest.dto;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public record ElectricServiceResponse(
    Long serviceNumber,
    Long clientId,
    String address,
    String status,
    LocalDate cutoffDate,
    boolean hasDebt,
    BigDecimal totalDebt,
    List<EnergyBillResponse> bills
) {}