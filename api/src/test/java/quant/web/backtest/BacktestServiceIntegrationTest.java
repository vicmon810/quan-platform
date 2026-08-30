// package 
package quant.web.backtest;

import static  org.assertj.core.api.Assertions.assertThat;
import java.math.BigDecimal;
import java.util.Map;
import java.util.UUID;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import quant.web.backtest.BacktestService;


@SpringBootTest
@ActiveProfiles("test")
@Transactional
public class BacktestServiceIntegrationTest {
    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private BacktestService service;

    @Test
    void createBacktestCreatesPendingRunForExistingAsset(){
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
                'BHP GROUP',
                'AUD',
                'EQUITY'
            )
            """
        );
        
        UUID publicId = service.createBacktest(
            "ASX",
            "BHP",
            "BuyAndHold",
            2020,
            2025,
            new BigDecimal("10000.00"),
            Map.<String, Object>of()
        );
        Map<String, Object> saved = jdbcTemplate.queryForMap(
            """
            SELECT
                br.public_id,
                br.status,
                br.strategy_name,
                br.strategy_version,
                br.start_date,
                br.end_date,
                br.initial_cash,
                a.exchange_code,
                a.symbol
            FROM
                quant.backtest_run AS br
            JOIN 
                quant.asset a
            ON 
                a.id = br.asset_id
            WHERE
                br.public_id = ?
            """
            ,
            publicId    
        );

        assertThat(saved.get("public_id")).isEqualTo(publicId);
        assertThat(saved.get("status")).isEqualTo("PENDING");
        assertThat(saved.get("strategy_name")).isEqualTo("BuyAndHold");
        assertThat(saved.get("strategy_version")).isEqualTo("1.0.0");
        assertThat(saved.get("exchange_code")).isEqualTo("ASX");
        assertThat(saved.get("symbol")).isEqualTo("BHP");
        assertThat((BigDecimal) saved.get("initial_cash"))
    .isEqualByComparingTo(new BigDecimal("10000.00"));
    }
}
