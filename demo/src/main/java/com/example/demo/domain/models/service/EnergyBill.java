package com.example.demo.domain.models.service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.YearMonth;
import lombok.Getter;
import lombok.NonNull;

@Getter
public class EnergyBill {
    private final String billNumber;
    private final BigDecimal amount;
    private final YearMonth period;
    private final LocalDate dueDate;
    private BillStatus status;
    private final ConsumptionDetail consumptionDetail;

    public EnergyBill(
        @NonNull String billNumber,
        @NonNull BigDecimal amount,
        @NonNull YearMonth period,
        @NonNull LocalDate dueDate,
        @NonNull BillStatus status,
        ConsumptionDetail consumptionDetail
    ) {
        this.billNumber = billNumber;
        this.amount = amount;
        this.period = period;
        this.dueDate = dueDate;
        this.status = status;
        this.consumptionDetail = consumptionDetail;
    }

    public EnergyBill(
        @NonNull String billNumber,
        @NonNull BigDecimal amount,
        @NonNull YearMonth period,
        @NonNull LocalDate dueDate,
        @NonNull BillStatus status
    ) {
        this(billNumber, amount, period, dueDate, status, null);
    }

    public boolean isUnpaid() {
        return this.status == BillStatus.UNPAID;
    }

    public void markAsPaid() {
        this.status = BillStatus.PAID;
    }
}
