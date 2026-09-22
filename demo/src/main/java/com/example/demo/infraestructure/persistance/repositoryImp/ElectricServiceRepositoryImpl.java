package com.example.demo.infraestructure.persistance.repositoryImp;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.stereotype.Component;

import com.example.demo.domain.models.service.ElectricService;
import com.example.demo.domain.models.service.EnergyBill;
import com.example.demo.domain.models.service.SupplyAddress;
import com.example.demo.domain.repository.ElectricServiceRepository;
import com.example.demo.infraestructure.persistance.entity.ElectricServiceJpaEntity;
import com.example.demo.infraestructure.persistance.entity.EnergyBillJpaEntity;
import com.example.demo.infraestructure.persistance.springData.SpringDataElectricServiceRepository;
import com.example.demo.domain.models.service.ConsumptionDetail;
import com.example.demo.infraestructure.persistance.entity.ConsumptionDetailEmbeddable;
import lombok.RequiredArgsConstructor;


@Component
@RequiredArgsConstructor
public class ElectricServiceRepositoryImpl implements ElectricServiceRepository {

    private final SpringDataElectricServiceRepository jpaRepository;

    @Override
    public ElectricService save(ElectricService service) {
        Optional<ElectricServiceJpaEntity> existingOpt = jpaRepository.findById(service.getServiceNumber());

        ElectricServiceJpaEntity entityToSave;

        if (existingOpt.isPresent()) {
            entityToSave = existingOpt.get();
            entityToSave.setClientId(service.getClientId());
            entityToSave.setAddress(service.getAddress().value());
            entityToSave.setStatus(service.getStatus());
            entityToSave.setCutoffDate(service.getCutoffDate());
        } else {
            entityToSave = toJpaEntity(service);
        }

        ElectricServiceJpaEntity saved = jpaRepository.save(entityToSave);
        return toDomain(saved);
    }

    @Override
    public Optional<ElectricService> findByServiceNumber(Long serviceNumber) {
        return jpaRepository.findById(serviceNumber)
            .map(this::toDomain);
    }

    private ElectricServiceJpaEntity toJpaEntity(ElectricService domain) {
        ElectricServiceJpaEntity entity = new ElectricServiceJpaEntity();
        entity.setServiceNumber(domain.getServiceNumber());
        entity.setClientId(domain.getClientId());
        entity.setAddress(domain.getAddress().value());
        entity.setStatus(domain.getStatus());
        entity.setCutoffDate(domain.getCutoffDate());

        if (domain.getBills() != null) {
            for (EnergyBill bill : domain.getBills()) {
                EnergyBillJpaEntity billEntity = new EnergyBillJpaEntity();
                billEntity.setBillNumber(bill.getBillNumber());
                billEntity.setAmount(bill.getAmount());
                billEntity.setPeriodFromYearMonth(bill.getPeriod());
                billEntity.setDueDate(bill.getDueDate());
                billEntity.setStatus(bill.getStatus());

                if (bill.getConsumptionDetail() != null) {
                    ConsumptionDetailEmbeddable detailEmbeddable = new ConsumptionDetailEmbeddable(
                        bill.getConsumptionDetail().activeCurrentReading(),
                        bill.getConsumptionDetail().activePreviousReading(),
                        bill.getConsumptionDetail().activeConsumptionKwh(),
                        bill.getConsumptionDetail().reactiveCurrentReading(),
                        bill.getConsumptionDetail().reactivePreviousReading(),
                        bill.getConsumptionDetail().cosPhi()
                    );
                    billEntity.setConsumptionDetail(detailEmbeddable);
                }

                entity.addBill(billEntity);
            }
        }

        return entity;
    }

    private ElectricService toDomain(ElectricServiceJpaEntity entity) {
        List<EnergyBill> bills = entity.getBills().stream()
            .map(b -> {
                ConsumptionDetail consumptionDetail = null;
                if (b.getConsumptionDetail() != null) {
                    consumptionDetail = new ConsumptionDetail(
                        b.getConsumptionDetail().getActiveCurrentReading(),
                        b.getConsumptionDetail().getActivePreviousReading(),
                        b.getConsumptionDetail().getActiveConsumptionKwh(),
                        b.getConsumptionDetail().getReactiveCurrentReading(),
                        b.getConsumptionDetail().getReactivePreviousReading(),
                        b.getConsumptionDetail().getCosPhi()
                    );
                }

                return new EnergyBill(
                    b.getBillNumber(),
                    b.getAmount(),
                    b.getPeriodAsYearMonth(),
                    b.getDueDate(),
                    b.getStatus(),
                    consumptionDetail
                );
            })
            .collect(Collectors.toList());

        return new ElectricService(
            entity.getServiceNumber(),
            entity.getClientId(),
            new SupplyAddress(entity.getAddress()),
            entity.getStatus(),
            entity.getCutoffDate(),
            bills
        );
    }
}
