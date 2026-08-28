package quant.web.backtest;

import java.math.BigDecimal;
import java.sql.ResultSet;
import java.time.LocalDate;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;


import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import tools.jackson.core.JacksonException;
import tools.jackson.databind.json.JsonMapper;


@Repository
public class BacktestRepository {

    private final JdbcTemplate jdbcTemplate;
    private final JsonMapper jsonMapper;

    public BacktestRepository(
        JdbcTemplate jdbcTemplate,
        JsonMapper jsonMapper
    ) {
        this.jdbcTemplate = jdbcTemplate;
        this.jsonMapper = jsonMapper;
    }

    public UUID createPendingRun(
        long assetId,
        String strategyName,
        String strategyVersion,
        LocalDate startDate,
        LocalDate endDate,
        BigDecimal initialCash,
        Map<String, Object> parameters
    ) {
        String parametersJson = toJson(parameters);

        String sql = """
            INSERT INTO quant.backtest_run (
                asset_id,
                strategy_name,
                strategy_version,
                start_date,
                end_date,
                initial_cash,
                parameters,
                status
            )
            VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                CAST(? AS jsonb),
                'PENDING'
            )
            RETURNING public_id
            """;

        return jdbcTemplate.queryForObject(
            sql,
            (resultSet, rowNumber) ->
                resultSet.getObject(
                    "public_id",
                    UUID.class
                ),
            assetId,
            strategyName,
            strategyVersion,
            startDate,
            endDate,
            initialCash,
            parametersJson
        );
    }

    private String toJson(
        Map<String, Object> parameters
    ) {
        try {
            return jsonMapper.writeValueAsString(
                parameters
            );
        } catch (JacksonException exception) {
            throw new IllegalArgumentException(
                "Backtest parameters cannot be serialized",
                exception
            );
        }
    }

    public Optional<Long> findAssetId(
        String exchangeCode,
        String symbol
    ){
        String sql = """
                SELECT 
                    id 
                FROM
                    quant.asset
                WHERE
                    exchange_code = ?
                And
                    symbol = ?
                """;
        
        return  jdbcTemplate.query(sql, 
            (ResultSet, rowNumber) -> 
            ResultSet.getLong("id"),
            exchangeCode,
            symbol
        )
        .stream()
        .findFirst();
    }

    public Optional<BacktestSummary> findSummaryByPublicId(UUID publicId){
        String sql = """
                SELECT
                    br.public_id,
                    br.status,
                    br.strategy_name,
                    br.start_date,
                    br.end_date,
                    br.initial_cash,
                    a.exchange_code,
                    a.symbol,
                    bm.backtest_run_id AS metric_run_id,
                    bm.final_value,
                    bm.cumulative_return,
                    bm.cagr,
                    bm.max_drawdown,
                    bm.daily_sharpe,
                    bm.calmar
                FROM
                    quant.backtest_run br
                JOIN
                    quant.asset a
                ON 
                    a.id = br.asset_id
                LEFT JOIN
                    quant.backtest_metric bm
                ON 
                    bm.backtest_run_id = br.id
                WHERE
                    br.public_id = ?
                """;
            
        return jdbcTemplate.query(
            sql,
            (resultSet, rowNumber) -> {    
                BacktestMetrics metrics = null;

                if (resultSet.getObject("metric_run_id") != null){
                    metrics = new BacktestMetrics(
                        resultSet.getBigDecimal("final_value"),
                         resultSet.getBigDecimal("cumulative_return"), 
                         resultSet.getBigDecimal("cagr"), 
                         resultSet.getBigDecimal("max_drawdown"), 
                         resultSet.getBigDecimal("daily_sharpe"), 
                         resultSet.getBigDecimal("calmar")
                    );
                }

                return new BacktestSummary(
                    resultSet.getObject("public_id", UUID.class),
                    resultSet.getString("status"),
                    resultSet.getString("exchange_code"),
                    resultSet.getString("symbol"),
                    resultSet.getString("strategy_name"),
                    resultSet.getObject("start_date", LocalDate.class),
                    resultSet.getObject("end_date",LocalDate.class),
                    resultSet.getBigDecimal("initial_cash"),
                    metrics
                );
            },
            publicId
        ).stream()
        .findFirst();
    }
}
