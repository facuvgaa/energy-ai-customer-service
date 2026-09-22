package com.example.demo.application.service.command;

public record AssociateServiceCommand(
    Long clientId,
    Long serviceNumber
) {
    public AssociateServiceCommand {
        if (clientId == null || clientId <= 0) {
            throw new IllegalArgumentException("The customer ID is required and must be positive.");
        }
        if (serviceNumber == null || serviceNumber <= 0) {
            throw new IllegalArgumentException("The service number must be positive.");
        }
    }
}