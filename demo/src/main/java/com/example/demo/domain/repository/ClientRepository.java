package com.example.demo.domain.repository;
import java.util.Optional;
import com.example.demo.domain.models.client.Client;
import com.example.demo.domain.models.client.Email;

public interface ClientRepository {
    Client save(Client client);
    Optional<Client> findById(Long id);
    Optional<Client> findByEmail(Email email);
}