package com.example.demo.infraestructure.persistance.entity;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.YearMonth;

import com.example.demo.domain.models.service.BillStatus;

import jakarta.persistence.Column;
import jakarta.persistence.Embedded;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "energy_bills")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class EnergyBillJpaEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "bill_number", nullable = false, unique = true, length = 50)
    private String billNumber;

    @Column(name = "amount", nullable = false, precision = 12, scale = 2)
    private BigDecimal amount;

    @Column(name = "period", nullable = false, length = 7)
    private String period;

    @Column(name = "due_date", nullable = false)
    private LocalDate dueDate;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 20)
    private BillStatus status;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "service_number", nullable = false)
    private ElectricServiceJpaEntity electricService;

    public YearMonth getPeriodAsYearMonth() {
        return YearMonth.parse(this.period);
    }

    public void setPeriodFromYearMonth(YearMonth yearMonth) {
        this.period = yearMonth.toString();
    }
    @Embedded
    private ConsumptionDetailEmbeddable consumptionDetail;
}