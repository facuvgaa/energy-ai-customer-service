package com.example.demo.application.client.usecase;
import java.util.ArrayList;

import org.springframework.stereotype.Service;

import com.example.demo.application.client.command.CreateClientCommand;
import com.example.demo.domain.models.client.Client;
import com.example.demo.domain.models.client.Email;
import com.example.demo.domain.repository.ClientRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public  class CreateClientUseCase {
    private final ClientRepository clientRepository;


    public  Long execute(CreateClientCommand command){
        Email email = new Email(command.email());

        clientRepository.findByEmail(email).ifPresent(existingClient -> {
            throw new IllegalStateException("Ya existe un cliente registrado con el email: " + command.email());
        });

        Client client = new Client(
            null,
            command.fullName(),
            email,
            new ArrayList<>()
        );

        Client savedClient = clientRepository.save(client);

        return savedClient.getId();
    }

    
}