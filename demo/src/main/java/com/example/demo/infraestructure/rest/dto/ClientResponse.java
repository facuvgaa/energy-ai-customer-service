package com.example.demo.infraestructure.rest.dto;

import java.util.List;

public record ClientResponse(
    Long id,
    String fullName,
    String email,
    List<Long> serviceNumbers
){}
    

