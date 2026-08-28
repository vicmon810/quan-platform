package quant.web.backtest;


import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
public class BacktestControllerIntegrationTest {
    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    void createBacktestResultAcceptedAndPendingRun() throws Exception{
        jdbcTemplate.update(
            """
            INSERT INTO 
                quant.asset(
                    exchange_code,
                    symbol,
                    data_symbol,
                    display_name,
                    currency_code,
                    asset_type
                )
            VALUES (
                'ASX',
                'BHP',
                'BHP.AX',
                'BHP Group',
                'AUD',
                'EQUITY'
            )
            """
        );

        mockMvc.perform(
            post("/api/backtests")
                .contentType(MediaType.APPLICATION_JSON)
                .content(
                    """
                    {
                        "exchangeCode":"ASX",
                        "symbol":"BHP",
                        "strategyName":"BuyAndHold",
                        "startYear":2020,
                        "endYear":2025,
                        "initialCash":10000,
                        "parameters":{}
                    }
                    """
                )
        ).andExpect(status().isAccepted())
        .andExpect(jsonPath("$.publicId").exists())
        .andExpect(jsonPath("$.status").value("PENDING"));
    }

    @Test 
    void createBacktestReturnsNotFoundWhenAssetDoesNotExist() 
    throws Exception{
        mockMvc.perform(
            post("/api/backtests")
            .contentType(MediaType.APPLICATION_JSON)
            .content(
            """
            {
                "exchangeCode": "ASX",
                "symbol": "DOES_NOT_EXIST",
                "strategyName": "BuyAndHold",
                "startYear": 2020,
                "endYear": 2025,
                "initialCash": 10000,
                "parameters": {}
            }
            """
        )
    ).andExpect(status().isNotFound());
    }

    @Test
    void createBacktestReturnsBadRequestWhenStartYearIsNotBeforeEndYear()
    throws Exception{
        mockMvc.perform(
            post("/api/backtests")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                            {
                                "exchangeCode": "ASX",
                                "symbol": "BHP",
                                "strategyName": "BuyAndHold",
                                "startYear": 2025,
                                "endYear": 2020,
                                "initialCash": 10000,
                                "parameters": {}
                            }
                        """)
        ).andExpect(status().isBadRequest());
    }

    @Test 
    void createBacktestReturnsBadRequestWhenInitialCashIsNotPositive() throws Exception{
        mockMvc.perform(
            post("/api/backtests")
            .contentType(MediaType.APPLICATION_JSON)
            .content(
                """
                {
                  "exchangeCode": "ASX",
                  "symbol": "BHP",
                  "strategyName": "BuyAndHold",
                  "startYear": 2020,
                  "endYear": 2025,
                  "initialCash": 0,
                  "parameters": {}
                }
                """
            )
        ).andExpect(status().isBadRequest());
    }
    
        @Test 
    void createBacktestReturnsBadRequestWhenExchangeCodeIsBlank() throws Exception{
        mockMvc.perform(
            post("/api/backtests")
            .contentType(MediaType.APPLICATION_JSON)
            .content(
                """
                {
                  "exchangeCode": "",
                  "symbol": "BHP",
                  "strategyName": "BuyAndHold",
                  "startYear": 2020,
                  "endYear": 2025,
                  "initialCash": 10,
                  "parameters": {}
                }
                """
            )
        ).andExpect(status().isBadRequest());
    }
    @Test 
    void createBacktestReturnsBadRequestWhenSymbolIsBlank() throws Exception{
        mockMvc.perform(
            post("/api/backtests")
            .contentType(MediaType.APPLICATION_JSON)
            .content(
                """
                {
                  "exchangeCode": "ASX",
                  "symbol": "",
                  "strategyName": "BuyAndHold",
                  "startYear": 2020,
                  "endYear": 2025,
                  "initialCash": 10,
                  "parameters": {}
                }
                """
            )
        ).andExpect(status().isBadRequest());
    }

    @Test 
    void createBacktestReturnsBadRequestWhenStrategyNameIsBlank() throws Exception{
        mockMvc.perform(
            post("/api/backtests")
            .contentType(MediaType.APPLICATION_JSON)
            .content(
                """
                {
                  "exchangeCode": "ASX",
                  "symbol": "BHP",
                  "strategyName": "",
                  "startYear": 2020,
                  "endYear": 2025,
                  "initialCash": 10,
                  "parameters": {}
                }
                """
            )
        ).andExpect(status().isBadRequest());
    }
}
