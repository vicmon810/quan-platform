package quant.web.backtest;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

// import org.hibernate.validator.constraints.UUID;
import java.util.UUID;
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
    void createBacktestResultAcceptedAndPendingRun() throws Exception {
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
                        """);

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
                                        """))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.publicId").exists())
                .andExpect(jsonPath("$.status").value("PENDING"));
    }

    @Test
    void createBacktestReturnsNotFoundWhenAssetDoesNotExist()
            throws Exception {
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
                                        """))
                .andExpect(status().isNotFound());
    }

    @Test
    void createBacktestReturnsBadRequestWhenStartYearIsNotBeforeEndYear()
            throws Exception {
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
                                """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void createBacktestReturnsBadRequestWhenInitialCashIsNotPositive() throws Exception {
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
                                        """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void createBacktestReturnsBadRequestWhenExchangeCodeIsBlank() throws Exception {
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
                                        """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void createBacktestReturnsBadRequestWhenSymbolIsBlank() throws Exception {
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
                                        """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void createBacktestReturnsBadRequestWhenStrategyNameIsBlank() throws Exception {
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
                                        """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void getBacktestReturnsCompletedBacktestWithMetrics()
            throws Exception {

        Long assetId = jdbcTemplate.queryForObject(
                """
                        INSERT INTO quant.asset (
                            exchange_code,
                            symbol,
                            data_symbol,
                            display_name,
                            currency_code,
                            asset_type
                        )
                        VALUES (
                            'NASDAQ_1',
                            'AAPL_1',
                            'AAPL_1',
                            'Apple Inc.',
                            'USD',
                            'EQUITY'
                        )
                        RETURNING id
                        """,
                Long.class);

        UUID publicId = jdbcTemplate.queryForObject(
                """
                        INSERT INTO quant.backtest_run (
                            asset_id,
                            strategy_name,
                            strategy_version,
                            start_date,
                            end_date,
                            initial_cash,
                            parameters,
                            status,
                            started_at,
                            completed_at
                        )
                        VALUES (
                            ?,
                            'BuyAndHold',
                            '1.0.0',
                            DATE '2020-01-01',
                            DATE '2025-01-01',
                            10000.00,
                            '{}'::jsonb,
                            'COMPLETED',
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        )
                        RETURNING public_id
                        """,
                UUID.class,
                assetId);

        Long runId = jdbcTemplate.queryForObject(
                """
                        SELECT id
                        FROM quant.backtest_run
                        WHERE public_id = ?
                        """,
                Long.class,
                publicId);

        jdbcTemplate.update(
                """
                        INSERT INTO quant.backtest_metric (
                            backtest_run_id,
                            final_value,
                            cumulative_return,
                            cagr,
                            max_drawdown,
                            daily_sharpe,
                            calmar,
                            market_exposure,
                            max_drawdown_duration_days,
                            average_drawdown_duration_days
                        )
                        VALUES (
                            ?,
                            19061.99,
                            0.906199,
                            0.137816,
                            0.317141,
                            0.753998,
                            0.434558,
                            0.951556,
                            120,
                            25.5
                        )
                        """,
                runId);

        mockMvc.perform(
                get("/api/backtests/{publicId}", publicId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.publicId")
                        .value(publicId.toString()))
                .andExpect(jsonPath("$.status")
                        .value("COMPLETED"))
                .andExpect(jsonPath("$.exchangeCode")
                        .value("NASDAQ_1"))
                .andExpect(jsonPath("$.symbol")
                        .value("AAPL_1"))
                .andExpect(jsonPath("$.strategyName")
                        .value("BuyAndHold"))
                .andExpect(jsonPath("$.startDate")
                        .value("2020-01-01"))
                .andExpect(jsonPath("$.endDate")
                        .value("2025-01-01"))
                .andExpect(jsonPath("$.initialCash")
                        .value(10000.00))
                .andExpect(jsonPath("$.metrics.finalValue")
                        .value(19061.99))
                .andExpect(jsonPath("$.metrics.cumulativeReturn")
                        .value(0.906199))
                .andExpect(jsonPath("$.metrics.cagr")
                        .value(0.137816))
                .andExpect(jsonPath("$.metrics.maxDrawdown")
                        .value(0.317141));
    }

    @Test
    void getBacktestReturnsNotFoundWhenBacktestDoesNotExist() throws Exception {
        UUID publicId = UUID.randomUUID();
        mockMvc.perform(
                get("/api/backtests/{publicId}", publicId)).andExpect(status().isNotFound());
    }

    @Test
    void getPortfolioValuesReturnsOrderedPortfolioValues()
            throws Exception {

        Long assetId = jdbcTemplate.queryForObject(
                """
                        INSERT INTO quant.asset (
                            exchange_code,
                            symbol,
                            data_symbol,
                            display_name,
                            currency_code,
                            asset_type
                        )
                        VALUES (
                            'NASDAQ_PORT',
                            'AAPL_PORT',
                            'AAPL_PORT',
                            'Apple Inc.',
                            'USD',
                            'EQUITY'
                        )
                        RETURNING id
                        """,
                Long.class);

        UUID publicId = jdbcTemplate.queryForObject(
                """
                        INSERT INTO quant.backtest_run (
                            asset_id,
                            strategy_name,
                            strategy_version,
                            start_date,
                            end_date,
                            initial_cash,
                            parameters,
                            status,
                            started_at,
                            completed_at
                        )
                        VALUES (
                            ?,
                            'BuyAndHold',
                            '1.0.0',
                            DATE '2020-01-01',
                            DATE '2025-01-01',
                            10000.00,
                            '{}'::jsonb,
                            'COMPLETED',
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP
                        )
                        RETURNING public_id
                        """,
                UUID.class,
                assetId);

        Long runId = jdbcTemplate.queryForObject(
                """
                        SELECT id
                        FROM quant.backtest_run
                        WHERE public_id = ?
                        """,
                Long.class,
                publicId);

        jdbcTemplate.update(
                """
                        INSERT INTO quant.portfolio_value (
                            backtest_run_id,
                            trading_date,
                            portfolio_value,
                            market_exposure,
                            drawdown
                        )
                        VALUES
                            (?, DATE '2020-01-03', 10100.00, 0.95, 0.01),
                            (?, DATE '2020-01-02', 10000.00, 0.00, 0.00)
                        """,
                runId,
                runId);

        mockMvc.perform(
                get(
                        "/api/backtests/{publicId}/portfolio-values",
                        publicId))
                .andExpect(status().isOk())
                .andExpect(
                        jsonPath("$.publicId")
                                .value(publicId.toString()))
                .andExpect(
                        jsonPath("$.values.length()")
                                .value(2))
                .andExpect(
                        jsonPath("$.values[0].date")
                                .value("2020-01-02"))
                .andExpect(
                        jsonPath("$.values[0].value")
                                .value(10000.00))
                .andExpect(
                        jsonPath("$.values[0].marketExposure")
                                .value(0.00))
                .andExpect(
                        jsonPath("$.values[0].drawdown")
                                .value(0.00))
                .andExpect(
                        jsonPath("$.values[1].date")
                                .value("2020-01-03"))
                .andExpect(
                        jsonPath("$.values[1].value")
                                .value(10100.00));
    }
}
