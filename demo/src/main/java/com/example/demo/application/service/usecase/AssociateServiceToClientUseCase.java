package com.example.demo.application.service.usecase;


import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;

import com.example.demo.application.service.command.AssociateServiceCommand;
import com.example.demo.domain.models.client.Client;
import com.example.demo.domain.models.service.ElectricService;
import com.example.demo.domain.repository.ClientRepository;
import com.example.demo.domain.repository.ElectricServiceRepository;

@Service
@RequiredArgsConstructor
public class AssociateServiceToClientUseCase {

    private final ClientRepository clientRepository;
    private final ElectricServiceRepository electricServiceRepository;

    @Transactional
    public void execute(AssociateServiceCommand command) {

        Client client = clientRepository.findById(command.clientId())
            .orElseThrow(() -> new IllegalArgumentException("No existe el cliente con ID: " + command.clientId()));


            ElectricService service = electricServiceRepository.findByServiceNumber(command.serviceNumber())
            .orElseThrow(() -> new IllegalArgumentException("No existe ningún suministro con el número: " + command.serviceNumber()));


            client.associateService(command.serviceNumber());
        service.assignToClient(command.clientId());


        clientRepository.save(client);
        electricServiceRepository.save(service);
    }
}
