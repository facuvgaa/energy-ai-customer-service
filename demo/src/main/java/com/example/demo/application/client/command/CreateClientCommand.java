package com.example.demo.application.client.command;

public record CreateClientCommand(
    String fullName,
    String email
) {
    public CreateClientCommand {
        if (fullName == null || fullName.isBlank()) {
            throw new IllegalArgumentException("the customer's name connot be empty");
        }
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("The customer's email address cannot be empty");
        }
        fullName = fullName.trim();
        email = email.trim();
    }
}