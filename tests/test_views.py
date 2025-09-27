import json
from unittest.mock import mock_open, patch

import pytest

import src.views


def test_main_views1(get_transactions_2: list) -> None:
    """Тест для функции main - норма"""
    test_cases = [
        ("12.01.2018 06:00:00", "Доброе утро!"),
        ("12.01.2018 11:00:00", "Добрый день!"),
        ("12.01.2018 17:00:00", "Добрый вечер!"),
        ("12.01.2018 23:00:00", "Доброй ночи!"),
    ]
    test_settings = {"user_currencies": ["USD"], "user_main_currency": "RUB", "user_stocks": ["AAPL"]}

    with (
        patch("builtins.input") as mock_input,
        patch("src.views.make_transactions", return_value=get_transactions_2),
        patch("src.views.filter_by_currency_month", return_value=get_transactions_2),
        patch("src.views.filtered_by_card_number", return_value=get_transactions_2),
        patch(
            "src.views.get_card_info",
            return_value=[
                {"last_digits": "4556", "total_spent": 88068.0, "cashback": 880.0},
            ],
        ),
        patch(
            "src.views.get_top_transactions",
            return_value={
                "top_transactions": [
                    {"date": "12.01.2018", "amount": -87068.0},
                ]
            },
        ),
        patch("builtins.open", mock_open(read_data=json.dumps(test_settings))),
        patch(
            "src.views.get_exchange_rate",
            return_value={
                "currencies": [
                    {"currency": "USD", "rate": 81.726},
                ]
            },
        ),
        patch(
            "src.views.get_stocks_rates",
            return_value={
                "stocks": [
                    {"stock": "AAPL", "price": "212.44"},
                ]
            },
        ),
    ):

        for hour, expected_greeting in test_cases:
            mock_input.return_value = hour
            result = src.views.main_views()

            assert expected_greeting in result
            assert "last_digits" in result
            assert "top_transactions" in result
            assert "currencies" in result
            assert "stocks" in result


def test_main_views2(get_transactions_2: list, capsys: pytest.CaptureFixture[str]) -> None:
    """Тест для функции main - введен неверный формат даты, нет данных за выбранный период"""

    test_settings = {"user_currencies": ["USD"], "user_main_currency": "RUB", "user_stocks": ["AAPL"]}

    with (
        patch("builtins.input", side_effect=["20/02/2023 12:00:00", "20.02.2023 12:00:00"]),
        patch("src.views.make_transactions", return_value=get_transactions_2),
        patch("builtins.open", mock_open(read_data=json.dumps(test_settings))),
        patch("src.views.get_exchange_rate", return_value={}),
        patch("src.views.get_stocks_rates", return_value={}),
    ):

        result = src.views.main_views()
        captured = capsys.readouterr()
        assert "Формат данных не соответствует запросу!" in captured.out
        assert "Данные о транзакциях за период отсутствуют" in result


def test_main_views3() -> None:
    """Тест для функции main - файл не найден, пуст или имеет не-xlsx формат"""
    with (
        patch("builtins.input", return_value="20.02.2023 12:00:00"),
        patch("src.views.make_transactions", return_value=[]),
    ):
        result = src.views.main_views()
        assert "Не удалось получить данные о транзакциях" in result


def test_main_logging(get_transactions_2: list, capsys: pytest.CaptureFixture[str]) -> None:
    """Тест проверяет запись в лог при завершении работы"""
    test_settings = {"user_currencies": ["USD"], "user_main_currency": "RUB", "user_stocks": ["AAPL"]}

    with (
        patch("builtins.input", return_value="20.02.2023 12:00:00"),
        patch("src.views.make_transactions", return_value=get_transactions_2),
        patch("builtins.open", mock_open(read_data=json.dumps(test_settings))),
        patch("src.views.views_logger.info") as mock_logger,
    ):
        src.views.main_views()
        mock_logger.assert_any_call("Ответ сформирован")
