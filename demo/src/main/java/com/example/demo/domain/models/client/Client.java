package com.example.demo.domain.models.client;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public  class Client {
    private  final Long id;
    private String fullName;
    private Email email;
    private final List<Long> serviceNumbers;

    public Client(Long id, String fullName, Email email, List<Long> serviceNumbers){
        if (fullName == null || fullName.isBlank()) {
            throw new IllegalArgumentException("The customer's full name is required");
        }
        if (email == null) {
            throw new IllegalArgumentException("the costumer email is required");
        }

        this.id = id;
        this.fullName = fullName;
        this.email = email;
        this.serviceNumbers = (serviceNumbers!=null) ? new ArrayList<>(serviceNumbers) : new ArrayList<>();
    }

    public void associateService(Long serviceNumber) {
        if (serviceNumber == null || serviceNumber <= 0) {
            throw new IllegalArgumentException("El número de servicio debe ser válido");
        }
        if (this.serviceNumbers.contains(serviceNumber)) {
            throw new IllegalStateException("El servicio " + serviceNumber + " ya está asociado a este cliente");
        }
        this.serviceNumbers.add(serviceNumber);
    }

    public void updateContactInfo(String newFullName, Email newEmail) {
        if (newFullName == null || newFullName.isBlank()) {
            throw new IllegalArgumentException("El nuevo nombre no puede estar vacío");
        }
        if (newEmail == null) {
            throw new IllegalArgumentException("El nuevo email no puede ser nulo");
        }
        this.fullName = newFullName.trim();
        this.email = newEmail;
    }

    public Long getId() { return id; }
    public String getFullName() { return fullName; }
    public Email getEmail() { return email; }
    public List<Long> getServiceNumbers() { return Collections.unmodifiableList(serviceNumbers); }
    
}