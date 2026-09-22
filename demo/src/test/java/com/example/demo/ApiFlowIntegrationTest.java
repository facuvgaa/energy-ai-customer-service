package com.example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import io.modelcontextprotocol.server.McpSyncServer;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class ApiFlowIntegrationTest {

    private static final String DESCRIPTION = "El transformador de la esquina tiro chispas y dejo a toda la cuadra sin luz electrica desde la tarde.";

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private McpSyncServer mcpSyncServer;

    @Test
    void restApisCoveredByMcpToolsWorkEndToEnd() throws Exception {
        mockMvc.perform(get("/api/services/522363"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.serviceNumber").value(522363))
                .andExpect(jsonPath("$.hasDebt").value(true))
                .andExpect(jsonPath("$.bills", hasSize(2)));

        MvcResult created = mockMvc.perform(post("/api/clients")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"fullName":"Ana Perez","email":"ana.perez@test.com"}
                                """))
                .andExpect(status().isCreated())
                .andExpect(header().string("Location", containsString("/api/clients/")))
                .andReturn();

        String location = created.getResponse().getHeader("Location");
        String clientId = location.substring(location.lastIndexOf('/') + 1);

        mockMvc.perform(get("/api/clients").param("email", "ana.perez@test.com"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(Long.parseLong(clientId)))
                .andExpect(jsonPath("$.fullName").value("Ana Perez"))
                .andExpect(jsonPath("$.email").value("ana.perez@test.com"));

        mockMvc.perform(post("/api/clients/" + clientId + "/services")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"serviceNumber":522363}
                                """))
                .andExpect(status().isNoContent());

        MvcResult claimResult = mockMvc.perform(post("/api/claim")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "serviceNumber": 522363,
                                  "description": "%s",
                                  "type": "URGENT"
                                }
                                """.formatted(DESCRIPTION)))
                .andExpect(status().isCreated())
                .andReturn();

        String claimNumber = claimResult.getResponse().getContentAsString();

        mockMvc.perform(get("/api/claim/" + claimNumber))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.claimNumber").value(claimNumber));

        mockMvc.perform(get("/api/claim/service/522363"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].claimNumber").value(claimNumber));
    }
}
