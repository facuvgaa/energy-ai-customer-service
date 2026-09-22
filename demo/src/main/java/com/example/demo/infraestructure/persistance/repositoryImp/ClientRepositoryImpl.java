package com.example.demo.infraestructure.persistance.repositoryImp;
import java.util.ArrayList;
import java.util.Optional;
import org.springframework.stereotype.Repository;

import lombok.RequiredArgsConstructor;

import com.example.demo.domain.models.client.Client;
import com.example.demo.domain.models.client.Email;
import  com.example.demo.domain.repository.ClientRepository;
import com.example.demo.infraestructure.persistance.entity.ClientJpaEntity;
import com.example.demo.infraestructure.persistance.springData.SpringDataClientRepository;

@Repository 
@RequiredArgsConstructor 
public class ClientRepositoryImpl implements ClientRepository {
    
    private  final SpringDataClientRepository JpaRepository;

    @Override 
    public Client save(Client client){
        ClientJpaEntity entity = new ClientJpaEntity(
            client.getId(),
            client.getFullName(),
            client.getEmail().value(),
            new ArrayList<>(client.getServiceNumbers())
        );

        ClientJpaEntity saved = JpaRepository.save(entity);

        return toDomain(saved);
    }

    @Override
    public Optional<Client> findById(Long id) {
        return JpaRepository.findById(id).map(this::toDomain);
    }

    @Override
    public Optional<Client> findByEmail(Email email) {
        return JpaRepository.findByEmail(email.value()).map(this::toDomain);
    }

    private Client toDomain(ClientJpaEntity entity) {
        return new Client(
            entity.getId(),
            entity.getFullName(),
            new Email(entity.getEmail()),
            entity.getServiceNumbers()
        );
    }
}
