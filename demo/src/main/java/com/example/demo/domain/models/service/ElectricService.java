package com.example.demo.domain.models.service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import lombok.Getter;
import lombok.NonNull;

@Getter
public class ElectricService {

    private final Long serviceNumber;
    private Long clientId;
    private SupplyAddress address;
    private ServiceStatus status;
    private LocalDate cutoffDate;
    private final List<EnergyBill> bills;

    public ElectricService(
        @NonNull Long serviceNumber,
        Long clientId,
        @NonNull SupplyAddress address,
        ServiceStatus status,
        LocalDate cutoffDate,
        List<EnergyBill> bills
    ) {
        if (serviceNumber <= 0) {
            throw new IllegalArgumentException("El número de servicio debe ser positivo");
        }

        this.serviceNumber = serviceNumber;
        this.clientId = clientId;
        this.address = address;
        this.status = (status != null) ? status : ServiceStatus.ACTIVE;
        this.cutoffDate = cutoffDate;
        this.bills = (bills != null) ? new ArrayList<>(bills) : new ArrayList<>();
    }

    public void assignToClient(@NonNull Long newClientId) {
        if (newClientId <= 0) {
            throw new IllegalArgumentException("El ID de cliente debe ser válido");
        }
        this.clientId = newClientId;
    }

    public void issueBill(@NonNull EnergyBill newBill) {
        boolean exists = bills.stream()
            .anyMatch(b -> b.getBillNumber().equalsIgnoreCase(newBill.getBillNumber()));

        if (exists) {
            throw new IllegalStateException("La factura " + newBill.getBillNumber() + " ya fue emitida para este servicio");
        }
        this.bills.add(newBill);
    }

    public void scheduleCutoff(@NonNull LocalDate date) {
        if (date.isBefore(LocalDate.now())) {
            throw new IllegalArgumentException("La fecha de corte no puede ser en el pasado");
        }
        this.cutoffDate = date;
    }

    public void suspendService() {
        this.status = ServiceStatus.SUSPENDED;
    }

    public BigDecimal calculateTotalDebt() {
        return bills.stream()
            .filter(EnergyBill::isUnpaid)
            .map(EnergyBill::getAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public boolean hasDebt() {
        return bills.stream().anyMatch(EnergyBill::isUnpaid);
    }

    public List<EnergyBill> getBills() {
        return Collections.unmodifiableList(bills);
    }
}
