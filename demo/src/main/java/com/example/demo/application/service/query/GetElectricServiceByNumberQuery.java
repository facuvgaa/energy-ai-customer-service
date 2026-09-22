package com.example.demo.application.service.query;

public record GetElectricServiceByNumberQuery(Long serviceNumber) {
    public GetElectricServiceByNumberQuery{
        if (serviceNumber == null || serviceNumber <= 0) {
            throw new IllegalArgumentException("The service number must be positive");
        }
    }
}
