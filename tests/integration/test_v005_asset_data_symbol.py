from typing import Any 
import pytest
from psycopg import Connection
from psycopg.errors import CheckViolation


pytestmark = pytest.mark.integration

def test_asset_store_data_symbol(
        db_connection: Connection[Any],
) -> None:
    row = db_connection.execute(
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
        VALUES(
            'ASX',
            'BHP',
            'BHP.AX',
            'BHP Group',
            'AUD',
            'EQUITY'
        )
        RETURNING
            exchange_code,
            symbol,
            data_symbol;
        """
    ).fetchone()

    assert row is not None
    assert row['exchange_code'] == 'ASX'
    assert row['symbol'] == 'BHP'
    assert row['data_symbol'] == 'BHP.AX'


def test_asset_reject_blank_data_symbol(
        db_connection: Connection[Any],
) -> None:
    with pytest.raises(
        CheckViolation,
        match="ck_asset_data_symbol_non_blank",
    ):
        db_connection.execute(
            """
            INSERT INTO 
                quant.asset
                    (
                        exchange_code,
                        symbol,
                        data_symbol,
                        display_name,
                        currency_code,
                        asset_type
                    )
            VALUES 
                (
                    'ASX',
                    'BHP',
                    '   ',
                    'BHP Group',
                    'AUD',
                    'EQUITY'
                );
            """
        )