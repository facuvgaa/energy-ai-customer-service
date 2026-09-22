package com.example.demo.application.service.usecase;

import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.example.demo.application.service.query.GetElectricServiceByNumberQuery;
import com.example.demo.domain.models.service.ElectricService;
import com.example.demo.domain.repository.ElectricServiceRepository;
import com.example.demo.infraestructure.rest.dto.ConsumptionDetailResponse;
import com.example.demo.infraestructure.rest.dto.ElectricServiceResponse;
import com.example.demo.infraestructure.rest.dto.EnergyBillResponse;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class GetElectricServiceByNumberUseCase {

    private final ElectricServiceRepository electricServiceRepository;

    @Transactional(readOnly = true)
    public ElectricServiceResponse execute(GetElectricServiceByNumberQuery query) {
        ElectricService service = electricServiceRepository.findByServiceNumber(query.serviceNumber())
            .orElseThrow(() -> new IllegalArgumentException("No existe el servicio con número: " + query.serviceNumber()));

        List<EnergyBillResponse> billResponses = service.getBills().stream()
            .map(b -> {
                ConsumptionDetailResponse detailResp = null;
                if (b.getConsumptionDetail() != null) {
                    detailResp = new ConsumptionDetailResponse(
                        b.getConsumptionDetail().activeCurrentReading(),
                        b.getConsumptionDetail().activePreviousReading(),
                        b.getConsumptionDetail().activeConsumptionKwh(),
                        b.getConsumptionDetail().reactiveCurrentReading(),
                        b.getConsumptionDetail().reactivePreviousReading(),
                        b.getConsumptionDetail().cosPhi()
                    );
                }
                return new EnergyBillResponse(
                    b.getBillNumber(),
                    b.getAmount(),
                    b.getPeriod().toString(),
                    b.getDueDate(),
                    b.getStatus().name(),
                    detailResp
                );
            })
            .toList();

        return new ElectricServiceResponse(
            service.getServiceNumber(),
            service.getClientId(),
            service.getAddress().value(),
            service.getStatus().name(),
            service.getCutoffDate(),
            service.hasDebt(),
            service.calculateTotalDebt(),
            billResponses
        );
    }
}


