package com.example.demo.application.client.usecase;

import org.springframework.stereotype.Service;

import com.example.demo.application.client.query.GetClientByEmailQuery;
import com.example.demo.domain.models.client.Email;
import com.example.demo.domain.repository.ClientRepository;
import com.example.demo.infraestructure.rest.dto.ClientResponse;

import org.springframework.transaction.annotation.Transactional;

import lombok.RequiredArgsConstructor;

@Service 
@RequiredArgsConstructor 
public class GetClientByEmailUseCase {
    private  final ClientRepository clientRepository;

    @Transactional(readOnly = true)
    public ClientResponse execute(GetClientByEmailQuery query) {
        Email email = new Email(query.email());

        return clientRepository.findByEmail(email)
            .map(client -> new ClientResponse(
                client.getId(),
                client.getFullName(),
                client.getEmail().value(),
                client.getServiceNumbers()
            ))
            .orElseThrow(() -> new IllegalArgumentException("No se encontró ningún usuario con el correo: " + query.email()));
    }
}
