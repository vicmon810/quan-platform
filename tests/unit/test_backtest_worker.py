from typing import Any 
import pytest 
from psycopg import Connection
from src.worker import backtest_worker

def test_run_worker_sleeps_when_queue_is_empty(
        monkeypatch: pytest.MonkeyPatch,
) -> None: 
    process_result = iter([
        False,
    ])

    sleep_calls: list[float] = []

    def fake_process_next_job(
            connection: Connection[Any],
    )-> bool:
        try:
            return next(process_result)
        except StopIteration:
            raise KeyboardInterrupt

    def fake_sleep(seconds:float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr(
        backtest_worker,
        'process_next_job',
        fake_process_next_job
    )

    monkeypatch,setattr(
        backtest_worker.time,
        'sleep',
        fake_sleep,
    )

    with pytest.raises(KeyboardInterrupt):
        backtest_worker.run_worker(
            connection = object(),
            poll_interval_seconds = 1.0,
        )

    assert sleep_calls == [1.0]



def test_run_worker_does_not_sleep_after_processing_job(
 monkeypatch: pytest.MonkeyPatch,       
) -> None:
    process_results = iter([True,])

    sleep_calls: list[float]= []

    def fake_process_next_job(
            connection:Connection[Any]
    ) -> bool:
        try:
            return next(process_results)
        except StopIteration:
            raise KeyboardInterrupt

    def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr(
        backtest_worker,
        'process_next_job',
        fake_process_next_job,
    )

    monkeypatch.setattr(
        backtest_worker.time,
        'sleep',
        fake_sleep,
    )

    with pytest.raises(KeyboardInterrupt):
        backtest_worker.run_worker(
            connection = object(),
            poll_interval_seconds = 1.0,
        )

    assert sleep_calls == []
    