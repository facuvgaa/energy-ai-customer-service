package com.example.demo.infraestructure.rest;

import org.springframework.web.bind.annotation.RestController;

import com.example.demo.application.client.command.CreateClientCommand;
import com.example.demo.application.client.query.GetClientByEmailQuery;
import com.example.demo.application.client.usecase.CreateClientUseCase;
import com.example.demo.application.client.usecase.GetClientByEmailUseCase;
import com.example.demo.application.service.command.AssociateServiceCommand;
import com.example.demo.application.service.usecase.AssociateServiceToClientUseCase;
import com.example.demo.infraestructure.rest.dto.AssociateServiceRequest;
import com.example.demo.infraestructure.rest.dto.ClientResponse;
import com.example.demo.infraestructure.rest.dto.CreateClientRequest;

import lombok.AllArgsConstructor;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.net.URI;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;



@RestController 
@RequestMapping("/api/clients")
@AllArgsConstructor 
public class ClientController {
    private  final CreateClientUseCase createClientUseCase;
    private final GetClientByEmailUseCase getClientByEmailUseCase;
    private final AssociateServiceToClientUseCase associateServiceToClientUseCase;

    @PostMapping
    public ResponseEntity<Void> createClient(@RequestBody CreateClientRequest request) {
        CreateClientCommand command = new CreateClientCommand(
            request.fullName(),
            request.email()
        );   

        Long clientId = createClientUseCase.execute(command);

        URI location = URI.create("/api/clients/" + clientId);
        return ResponseEntity.created(location).build();
    }
    @GetMapping
    public ResponseEntity<ClientResponse> getClientByEmail(@RequestParam String email) {
        GetClientByEmailQuery query = new GetClientByEmailQuery(email);
        ClientResponse response = getClientByEmailUseCase.execute(query);
        return ResponseEntity.ok(response);
    }  

    @PostMapping("/{id}/services")
    public ResponseEntity<Void> associateService(
        @PathVariable Long id,
        @RequestBody AssociateServiceRequest request
    ) {
        AssociateServiceCommand command = new AssociateServiceCommand(id, request.serviceNumber());
        associateServiceToClientUseCase.execute(command);
        return ResponseEntity.noContent().build();  
    }
}
