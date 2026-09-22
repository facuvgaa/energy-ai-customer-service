package com.example.demo.infraestructure.mcp;

import java.util.List;
import java.util.Map;

import org.springframework.boot.web.servlet.ServletRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.example.demo.application.claim.command.CreateClaimCommand;
import com.example.demo.application.claim.query.GetClaimByNumberQuery;
import com.example.demo.application.claim.query.GetClaimsByServiceNumberQuery;
import com.example.demo.application.claim.usecase.CreateClaimUseCase;
import com.example.demo.application.claim.usecase.GetClaimByNumberUseCase;
import com.example.demo.application.claim.usecase.GetClaimsByServiceNumberUseCase;
import com.example.demo.application.client.command.CreateClientCommand;
import com.example.demo.application.client.query.GetClientByEmailQuery;
import com.example.demo.application.client.usecase.CreateClientUseCase;
import com.example.demo.application.client.usecase.GetClientByEmailUseCase;
import com.example.demo.application.service.command.AssociateServiceCommand;
import com.example.demo.application.service.query.GetElectricServiceByNumberQuery;
import com.example.demo.application.service.usecase.AssociateServiceToClientUseCase;
import com.example.demo.application.service.usecase.GetElectricServiceByNumberUseCase;
import com.example.demo.domain.models.claims.Claim;
import com.example.demo.domain.models.claims.ClaimType;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.modelcontextprotocol.json.jackson2.JacksonMcpJsonMapper;
import io.modelcontextprotocol.server.McpServer;
import io.modelcontextprotocol.server.McpSyncServer;
import io.modelcontextprotocol.server.transport.HttpServletStreamableServerTransportProvider;
import io.modelcontextprotocol.spec.McpSchema.CallToolResult;
import io.modelcontextprotocol.spec.McpSchema.ServerCapabilities;
import io.modelcontextprotocol.spec.McpSchema.Tool;
import jakarta.servlet.http.HttpServlet;

@Configuration
public class McpServerConfig {

    @Bean
    public HttpServletStreamableServerTransportProvider transportProvider(ObjectMapper springObjectMapper) {
        return HttpServletStreamableServerTransportProvider.builder()
                .jsonMapper(new JacksonMcpJsonMapper(springObjectMapper))
                .build();
    }

    @Bean
    public ServletRegistrationBean<HttpServlet> mcpServlet(HttpServletStreamableServerTransportProvider transportProvider) {
        ServletRegistrationBean<HttpServlet> reg = new ServletRegistrationBean<>(transportProvider, "/mcp", "/mcp/*");
        reg.setAsyncSupported(true);
        return reg;
    }

    @Bean
    public McpSyncServer mcpSyncServer(
            HttpServletStreamableServerTransportProvider transportProvider,
            ObjectMapper springObjectMapper,
            CreateClaimUseCase createClaimUseCase,
            GetClaimByNumberUseCase getClaimByNumberUseCase,
            GetClaimsByServiceNumberUseCase getClaimsByServiceNumberUseCase,
            AssociateServiceToClientUseCase associateServiceToClientUseCase,
            CreateClientUseCase createClientUseCase,
            GetClientByEmailUseCase getClientByEmailUseCase,
            GetElectricServiceByNumberUseCase getElectricServiceByNumberUseCase) {

        var jsonMapper = new JacksonMcpJsonMapper(springObjectMapper);

        Tool createClaimTool = Tool.builder("create_claim", jsonMapper, """
                {
                  "type": "object",
                  "properties": {
                    "serviceNumber": { "type": "integer", "description": "Número de suministro eléctrico (ej: 522363)" },
                    "description": { "type": "string", "description": "Detalle del incidente (mínimo 80 caracteres)" },
                    "type": { "type": "string", "enum": ["URGENT", "RECONNECTION", "BILLING_CLAIM"], "description": "Tipo de reclamo" }
                  },
                  "required": ["serviceNumber", "description", "type"]
                }
                """)
                .description("Registra un reclamo técnico o comercial. La descripción debe tener al menos 80 caracteres.")
                .build();

        Tool getClaimTool = Tool.builder("get_claim_by_number", jsonMapper, """
                {
                  "type": "object",
                  "properties": {
                    "claimNumber": { "type": "string", "description": "Código del reclamo" }
                  },
                  "required": ["claimNumber"]
                }
                """)
                .description("Consulta el estado y detalle de un reclamo por su código unívoco (CLM-XXXXXXXX).")
                .build();

        Tool getClaimsByServiceTool = Tool.builder("get_claims_by_service", jsonMapper, """
                {
                  "type": "object",
                  "properties": {
                    "serviceNumber": { "type": "integer", "description": "Número del suministro" }
                  },
                  "required": ["serviceNumber"]
                }
                """)
                .description("Lista todos los reclamos asociados a un número de suministro eléctrico.")
                .build();

        Tool associateServiceTool = Tool.builder("associate_service_to_client", jsonMapper, """
                {
                  "type": "object",
                  "properties": {
                    "clientId": { "type": "integer", "description": "Número de cliente" },
                    "serviceNumber": { "type": "integer", "description": "Número de servicio" }
                  },
                  "required": ["clientId", "serviceNumber"]
                }
                """)
                .description("Asocia un servicio a un cliente.")
                .build();

        Tool createClientTool = Tool.builder("create_client", jsonMapper, """
                {
                  "type": "object",
                  "properties": {
                    "fullName": { "type": "string", "description": "Nombre completo del cliente" },
                    "email": { "type": "string", "description": "Email del cliente" }
                  },
                  "required": ["fullName", "email"]
                }
                """)
                .description("Registra un cliente nuevo.")
                .build();

        Tool getClientByEmailTool = Tool.builder("get_client_by_email", jsonMapper, """
                {
                  "type": "object",
                  "properties": {
                    "email": { "type": "string", "description": "Email del cliente" }
                  },
                  "required": ["email"]
                }
                """)
                .description("Consulta un cliente por email.")
                .build();

        Tool getElectricServiceTool = Tool.builder("get_electric_service_by_number", jsonMapper, """
                {
                  "type": "object",
                  "properties": {
                    "serviceNumber": { "type": "integer", "description": "Número de suministro eléctrico" }
                  },
                  "required": ["serviceNumber"]
                }
                """)
                .description("Consulta un suministro eléctrico, deudas y facturas.")
                .build();

        // Inicializamos McpServer con transportProvider (NO con Stdio)
        return McpServer.sync(transportProvider)
                .serverInfo("electric-claims-server", "1.0.0")
                .capabilities(ServerCapabilities.builder().tools(true).build())
                .toolCall(createClaimTool, (exchange, request) -> {
                    try {
                        Map<String, Object> arguments = request.arguments();
                        Long serviceNumber = ((Number) arguments.get("serviceNumber")).longValue();
                        String description = (String) arguments.get("description");
                        ClaimType type = ClaimType.valueOf((String) arguments.get("type"));

                        String claimNumber = createClaimUseCase.execute(
                                new CreateClaimCommand(serviceNumber, description, type));

                        return success("Reclamo creado exitosamente con ID: " + claimNumber);
                    } catch (Exception ex) {
                        return error("Error al crear el reclamo: " + ex.getMessage());
                    }
                })
                .toolCall(getClaimTool, (exchange, request) -> {
                    try {
                        String claimNumber = (String) request.arguments().get("claimNumber");
                        Claim claim = getClaimByNumberUseCase.execute(new GetClaimByNumberQuery(claimNumber));
                        return success(claim.toString());
                    } catch (Exception ex) {
                        return error("Error: " + ex.getMessage());
                    }
                })
                .toolCall(getClaimsByServiceTool, (exchange, request) -> {
                    try {
                        Long serviceNumber = ((Number) request.arguments().get("serviceNumber")).longValue();
                        List<Claim> claims = getClaimsByServiceNumberUseCase.execute(
                                new GetClaimsByServiceNumberQuery(serviceNumber));
                        return success(claims.toString());
                    } catch (Exception ex) {
                        return error("Error: " + ex.getMessage());
                    }
                })
                .toolCall(associateServiceTool, (exchange, request) -> {
                    try {
                        Map<String, Object> arguments = request.arguments();
                        Long clientId = ((Number) arguments.get("clientId")).longValue();
                        Long serviceNumber = ((Number) arguments.get("serviceNumber")).longValue();

                        associateServiceToClientUseCase.execute(
                                new AssociateServiceCommand(clientId, serviceNumber));

                        return success("El servicio " + serviceNumber
                                + " fue asociado exitosamente al cliente ID " + clientId + ".");
                    } catch (Exception ex) {
                        return error("Error al asociar el servicio: " + ex.getMessage());
                    }
                })
                .toolCall(createClientTool, (exchange, request) -> {
                    try {
                        Map<String, Object> arguments = request.arguments();
                        Long clientId = createClientUseCase.execute(new CreateClientCommand(
                                (String) arguments.get("fullName"),
                                (String) arguments.get("email")));
                        return success("Cliente creado exitosamente con ID: " + clientId);
                    } catch (Exception ex) {
                        return error("Error al crear el cliente: " + ex.getMessage());
                    }
                })
                .toolCall(getClientByEmailTool, (exchange, request) -> {
                    try {
                        var client = getClientByEmailUseCase.execute(
                                new GetClientByEmailQuery((String) request.arguments().get("email")));
                        return success(client.toString());
                    } catch (Exception ex) {
                        return error("Error: " + ex.getMessage());
                    }
                })
                .toolCall(getElectricServiceTool, (exchange, request) -> {
                    try {
                        Long serviceNumber = ((Number) request.arguments().get("serviceNumber")).longValue();
                        var service = getElectricServiceByNumberUseCase.execute(
                                new GetElectricServiceByNumberQuery(serviceNumber));
                        return success(service.toString());
                    } catch (Exception ex) {
                        return error("Error: " + ex.getMessage());
                    }
                })
                .build();
    }

    private static CallToolResult success(String text) {
        return CallToolResult.builder()
                .addTextContent(text)
                .isError(false)
                .build();
    }

    private static CallToolResult error(String text) {
        return CallToolResult.builder()
                .addTextContent(text)
                .isError(true)
                .build();
    }
}
