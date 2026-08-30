package quant.web.backtest;
// package quant.web.backtest;
// package quant.web.backtest;
import static org.assertj.core.api.Assertions.assertThat;


import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Map;
import java.util.UUID;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest 
@ActiveProfiles("test")
@Transactional 
class  BacktestRepositoryIntegrationTest{
    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private  BacktestRepository repository;
    

    @Test 
    void createPendingRunCreatesPendingBacktestForExistingAsset(){
        Long assetId = jdbcTemplate.queryForObject(
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
            'ASX_TEST',
            'BHP_TEST',
            'BHP.AX_TEST',
            'BHP Group',
            'AUD',
            'EQUITY'
        )
        RETURNING id
        """, 
        Long.class
    );

    UUID publicId = repository.createPendingRun(
        assetId,
        "BuyAndHold",
        "1.0.0",
        LocalDate.of(2020,1,1),
        LocalDate.of(2025,1,1),
        new BigDecimal("10000.00"),
        Map.<String, Object>of()
    );

    Map<String, Object> saved = jdbcTemplate.queryForMap(
        """
        SELECT 
            public_id,
            status,
            strategy_name,
            initial_cash
        FROM
            quant.backtest_run
        WHERE
            public_id = ?
        """,
        publicId
        );
    
    assertThat(saved.get("status")).isEqualTo("PENDING");
    assertThat(saved.get("strategy_name")).isEqualTo("BuyAndHold");
    assertThat(saved.get("public_id")).isEqualTo(publicId);
    assertThat((BigDecimal) saved.get("initial_cash")).isEqualByComparingTo(new BigDecimal("10000"));

    }

    @Test 
	void finalAssetIdReturnsIdForExistingAsset(){
		Long expectedAssetId = jdbcTemplate.queryForObject(
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
				'CBA',
				'CBA.AX',
				'Commonwealth Bank',
				'AUD',
				'EQUITY'
			)
			RETURNING 
				id
			""",
			Long.class
		);

		var actualAssetId = repository.findAssetId(
			"ASX",
			"CBA"
		);

		assertThat(actualAssetId).contains(expectedAssetId);
	}

    @Test
    void findAssetIdReturnsEmptyWhenAssetDoesNotExist(){
        var assetId = repository.findAssetId(
            "ASX",
            "DOES_NOT_EXIST"
        );
        assertThat(assetId).isEmpty();
    }

    @Test 
    void findSummaryByPublicIdReturnsCompletedBacktestWithMetrics(){
        Long assetId = jdbcTemplate.queryForObject(
            """
            INSERT INTO
                quant.asset (
                    exchange_code,
                    symbol,
                    data_symbol,
                    display_name,
                    currency_code,
                    asset_type
                )
            VALUES(
                'NASDAQ_TEST',
                'AAPL_TEST',
                'AAPL_TEST',
                'APPLE Inc. TEST',
                'USD',
                'EQUITY'
            )
            RETURNING 
                id
            """, Long.class
        );

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
        assetId
    );

    Long runId = jdbcTemplate.queryForObject(
        """
        SELECT id
        FROM quant.backtest_run
        WHERE public_id = ?
        """,
        Long.class,
        publicId
    );

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
        runId
    );

    var summary = repository
        .findSummaryByPublicId(publicId)
        .orElseThrow();

    assertThat(summary.publicId())
        .isEqualTo(publicId);

    assertThat(summary.status())
        .isEqualTo("COMPLETED");

    assertThat(summary.exchangeCode())
        .isEqualTo("NASDAQ_TEST");

    assertThat(summary.symbol())
        .isEqualTo("AAPL_TEST");

    assertThat(summary.strategyName())
        .isEqualTo("BuyAndHold");

    assertThat(summary.startDate())
        .isEqualTo(LocalDate.of(2020, 1, 1));

    assertThat(summary.endDate())
        .isEqualTo(LocalDate.of(2025, 1, 1));

    assertThat(summary.initialCash())
        .isEqualByComparingTo(
            new BigDecimal("10000.00")
        );

    assertThat(summary.metrics())
        .isNotNull();

    assertThat(summary.metrics().finalValue())
        .isEqualByComparingTo(
            new BigDecimal("19061.99")
        );

    assertThat(summary.metrics().cumulativeReturn())
        .isEqualByComparingTo(
            new BigDecimal("0.906199")
        );

    assertThat(summary.metrics().cagr())
        .isEqualByComparingTo(
            new BigDecimal("0.137816")
        );

    assertThat(summary.metrics().maxDrawdown())
        .isEqualByComparingTo(
            new BigDecimal("0.317141")
        );
    }

    @Test
    void findSummaryByPublicIdReturnsPendingBacktestWithoutMetrics(){
        Long assetId = jdbcTemplate.queryForObject("""
            INSERT INTO
                quant.asset
                    (exchange_code,
                    symbol,
                    data_symbol,
                    display_name,
                    currency_code,
                    asset_type)
            VALUES(
                'NASDAQ_TEST',
                'MSFT_TEST',
                'MSFT_TEST',
                'Microsoft',
                'USD',
                'EQUITY'
            )
            RETURNING 
                id;
            """, Long.class);

            UUID publicId = jdbcTemplate.queryForObject("""
                INSERT INTO
                    quant.backtest_run
                        (asset_id,
                        strategy_name,
                        strategy_version,
                        start_date,
                        end_date,
                        initial_cash,
                        parameters,
                        status)
                VALUES 
                    (?,
                    'BuyAndHold',
                    '1.0.0',
                    DATE '2020-01-01',
                    DATE '2024-01-01',
                    10000.00,
                    '{}'::jsonb,
                    'PENDING')
                RETURNING 
                    public_id
                """, UUID.class, assetId);

            var summary = repository
            .findSummaryByPublicId(publicId).orElseThrow();

            assertThat(summary.publicId()).isEqualTo(publicId);
            assertThat(summary.status()).isEqualTo("PENDING");
            assertThat(summary.exchangeCode()).isEqualTo("NASDAQ_TEST");
            assertThat(summary.symbol()).isEqualTo("MSFT_TEST");
            assertThat(summary.strategyName()).isEqualTo("BuyAndHold");
            assertThat(summary.metrics()).isNull();

    }

    @Test
void findPortfolioValuesByPublicIdReturnsValuesOrderedByTradingDate() {
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
            'NASDAQ_R',
            'AAPL_R',
            'AAPL_R',
            'Apple Inc.',
            'USD',
            'EQUITY'
        )
        RETURNING id
        """,
        Long.class
    );

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
        assetId
    );

    Long runId = jdbcTemplate.queryForObject(
        """
        SELECT id
        FROM quant.backtest_run
        WHERE public_id = ?
        """,
        Long.class,
        publicId
    );

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
        runId
    );

    var values =
        repository.findPortfolioValuesByPublicId(publicId);

    assertThat(values)
        .hasSize(2);

    assertThat(values.get(0).date())
        .isEqualTo(LocalDate.of(2020, 1, 2));

    assertThat(values.get(0).value())
        .isEqualByComparingTo(
            new BigDecimal("10000.00")
        );

    assertThat(values.get(0).marketExposure())
        .isEqualByComparingTo(
            new BigDecimal("0.00")
        );

    assertThat(values.get(0).drawdown())
        .isEqualByComparingTo(
            new BigDecimal("0.00")
        );

    assertThat(values.get(1).date())
        .isEqualTo(LocalDate.of(2020, 1, 3));

    assertThat(values.get(1).value())
        .isEqualByComparingTo(
            new BigDecimal("10100.00")
        );
}
}