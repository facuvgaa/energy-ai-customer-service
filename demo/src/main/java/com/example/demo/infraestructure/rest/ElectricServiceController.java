package com.example.demo.infraestructure.rest;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.application.service.query.GetElectricServiceByNumberQuery;
import com.example.demo.application.service.usecase.GetElectricServiceByNumberUseCase;
import com.example.demo.infraestructure.rest.dto.ElectricServiceResponse;

import lombok.RequiredArgsConstructor;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;



@RestController 
@RequestMapping("/api/services")
@RequiredArgsConstructor 
public class ElectricServiceController {
    private final GetElectricServiceByNumberUseCase getElectricServiceByNumberUseCase;

    @GetMapping("/{serviceNumber}")
    public ResponseEntity<ElectricServiceResponse> getServiceByNumber(@PathVariable("serviceNumber")  Long serviceNumber) {
        GetElectricServiceByNumberQuery query = new  GetElectricServiceByNumberQuery(serviceNumber);
        ElectricServiceResponse response = getElectricServiceByNumberUseCase.execute(query);
        return ResponseEntity.ok(response);
    }
    
}
