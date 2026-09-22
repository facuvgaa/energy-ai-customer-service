package com.example.demo;

import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.example.demo.application.claim.command.CreateClaimCommand;
import com.example.demo.application.claim.usecase.CreateClaimUseCase;
import com.example.demo.domain.models.claims.Claim;
import com.example.demo.domain.models.claims.ClaimType;
import com.example.demo.domain.models.service.ElectricService;
import com.example.demo.domain.repository.ClaimRepository;
import com.example.demo.domain.repository.ElectricServiceRepository;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DemoApplicationTests {

    @Mock
    private ClaimRepository claimRepository;

    @Mock
    private ElectricServiceRepository electricServiceRepository;

    @InjectMocks
    private CreateClaimUseCase createClaimUseCase;

    private final String validDescription = "El transformador de la esquina tiro chispas y dejo a toda la cuadra sin luz electrica desde la tarde.";

    @Test
    void shouldCreateClaimSuccessfullyWhenServiceExists() {
        // GIVEN: El servicio eléctrico existe (mockeado para no lidiar con constructor complejo)
        Long serviceNumber = 123456L;
        ElectricService mockService = mock(ElectricService.class);
        when(electricServiceRepository.findByServiceNumber(serviceNumber))
            .thenReturn(Optional.of(mockService));

        // Simulamos que el repositorio guarda y devuelve la entidad
        when(claimRepository.save(any(Claim.class))).thenAnswer(invocation -> invocation.getArgument(0));

        CreateClaimCommand command = new CreateClaimCommand(
            serviceNumber,
            validDescription,
            ClaimType.URGENT
        );

        // WHEN: Ejecutamos el caso de uso
        String claimNumber = createClaimUseCase.execute(command);

        // THEN: Devuelve un claimNumber con el formato esperado y se llama al save
        assertNotNull(claimNumber);
        assertTrue(claimNumber.startsWith("CLM-"));
        verify(claimRepository, times(1)).save(any(Claim.class));
    }

    @Test
    void shouldFailWhenElectricServiceDoesNotExist() {
        // GIVEN: El servicio no existe en el sistema
        Long serviceNumber = 999999L;
        when(electricServiceRepository.findByServiceNumber(serviceNumber))
            .thenReturn(Optional.empty());

        CreateClaimCommand command = new CreateClaimCommand(
            serviceNumber,
            validDescription,
            ClaimType.URGENT
        );

        // WHEN & THEN: Esperamos la excepción de negocio
        assertThrows(IllegalArgumentException.class, () -> {
            createClaimUseCase.execute(command);
        });

        // Aseguramos que nunca intentó guardar nada
        verify(claimRepository, never()).save(any());
    }

    @Test
    void shouldFailWhenDescriptionIsTooShort() {
        // GIVEN: Servicio válido pero descripción corta (< 80 caracteres)
        Long serviceNumber = 123456L;
        ElectricService mockService = mock(ElectricService.class);
        when(electricServiceRepository.findByServiceNumber(serviceNumber))
            .thenReturn(Optional.of(mockService));

        CreateClaimCommand command = new CreateClaimCommand(
            serviceNumber,
            "Corte de luz en casa", // Muy corta
            ClaimType.URGENT
        );

        // WHEN & THEN: Falla por regla de dominio
        assertThrows(IllegalArgumentException.class, () -> {
            createClaimUseCase.execute(command);
        });

        verify(claimRepository, never()).save(any());
    }
}