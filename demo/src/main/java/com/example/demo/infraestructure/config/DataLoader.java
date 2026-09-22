package com.example.demo.infraestructure.config;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.ArrayList;

import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import com.example.demo.domain.models.service.BillStatus;
import com.example.demo.domain.models.service.ConsumptionDetail;
import com.example.demo.domain.models.service.ElectricService;
import com.example.demo.domain.models.service.EnergyBill;
import com.example.demo.domain.models.service.ServiceStatus;
import com.example.demo.domain.models.service.SupplyAddress;
import com.example.demo.domain.repository.ElectricServiceRepository;

import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class DataLoader implements CommandLineRunner {

    private final ElectricServiceRepository electricServiceRepository;

    @Override
    public void run(String... args) throws Exception {
        // 1. Detalle de consumo extraído de la factura (Activa: 50.095 - 49.820 = 275 kWh | Reactiva: 9.235 - 9.234 | Cos Phi: 1.00)
        ConsumptionDetail consumption = new ConsumptionDetail(
            new BigDecimal("50.095"),
            new BigDecimal("49.820"),
            new BigDecimal("275.000"),
            new BigDecimal("9.235"),
            new BigDecimal("9.234"),
            new BigDecimal("1.00")
        );

        // 2. Factura de julio (PAGADA, sin detalle cargado)
        EnergyBill billJuly = new EnergyBill(
            "FAC-202607-00522363",
            new BigDecimal("12450.00"),
            YearMonth.of(2026, 7),
            LocalDate.of(2026, 8, 10),
            BillStatus.PAID,
            null
        );

        // 3. Factura de agosto (IMPAGA, con el desglose técnico de consumo)
        EnergyBill billAugust = new EnergyBill(
            "FAC-202608-00522363",
            new BigDecimal("15890.50"),
            YearMonth.of(2026, 8),
            LocalDate.of(2026, 9, 10),
            BillStatus.UNPAID,
            consumption
        );

        // 4. Suministro eléctrico (sin cliente asignado aún)
        ElectricService service = new ElectricService(
            522363L,
            null,
            new SupplyAddress("San Martín 450"),
            ServiceStatus.ACTIVE,
            LocalDate.of(2026, 9, 25),
            new ArrayList<>()
        );

        // 5. Emitir facturas dentro del agregado
        service.issueBill(billJuly);
        service.issueBill(billAugust);

        // 6. Guardar en H2
        electricServiceRepository.save(service);

        System.out.println(">>> [DataLoader] Suministro 522363 precargado con métricas de consumo en H2 <<<");
    }
}