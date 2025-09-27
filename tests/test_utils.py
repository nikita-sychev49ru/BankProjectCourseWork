import os
from typing import Any
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import (
    filter_by_currency_month,
    filtered_by_card_number,
    get_card_info,
    get_exchange_rate,
    get_stocks_rates,
    get_top_transactions,
    make_transactions,
)


def test_make_transactions1() -> None:
    """тест для функции, считывающей транзакции из файла .xlsx - норма"""
    data_frame = pd.DataFrame({"name": ["Ann", "Bob"], "age": [25, 31], "city": ["NY", "LA"]})
    with patch("pandas.read_excel", return_value=data_frame):
        result = make_transactions()
    assert result[0] == {"name": "Ann", "age": 25, "city": "NY"}


def test_make_transactions2(capsys: pytest.CaptureFixture[str]) -> None:
    """тест для функции, считывающей транзакции из файла .xlsx -
    файл или папка не найдены"""
    make_transactions("../date/operations.xlsx")
    print_result = capsys.readouterr()
    expect_result = "Ошибка! Файл не найден!"
    assert print_result.out.strip() == expect_result


def test_make_transactions3(capsys: pytest.CaptureFixture[str]) -> None:
    """тест для функции, считывающей транзакции из файла .xlsx -
    файл имеет формат, отличный от .xlsx"""
    file_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(file_dir, "..", "user_settings.json")
    make_transactions(file_path)
    print_result = capsys.readouterr()
    expect_result = "Данные имеют неверный формат!"
    assert print_result.out.strip() == expect_result


@pytest.mark.parametrize(
    "act_date, result",
    [
        (
            "12.01.2018",
            [
                {
                    "Дата операции": "10.01.2018 12:41:24",
                    "Номер карты": "*5441",
                    "Статус": "OK",
                    "Сумма платежа": -567.53,
                    "Кэшбэк": 5.0,
                },
                {
                    "Дата операции": "12.01.2018 11:10:05",
                    "Номер карты": "*4556",
                    "Статус": "OK",
                    "Сумма платежа": -87068.0,
                    "Кэшбэк": 870.00,
                },
            ],
        ),
        (
            "15.01.2018",
            [
                {
                    "Дата операции": "10.01.2018 12:41:24",
                    "Номер карты": "*5441",
                    "Статус": "OK",
                    "Сумма платежа": -567.53,
                    "Кэшбэк": 5.0,
                },
                {
                    "Дата операции": "12.01.2018 11:10:05",
                    "Номер карты": "*4556",
                    "Статус": "OK",
                    "Сумма платежа": -87068.0,
                    "Кэшбэк": 870.00,
                },
                {
                    "Дата операции": "15.01.2018 08:15:55",
                    "Номер карты": "*4556",
                    "Статус": "OK",
                    "Сумма платежа": -1000.0,
                    "Кэшбэк": 10,
                },
            ],
        ),
        ("12.00.2018", []),
    ],
)
def test_filter_by_currency_month1(get_transactions: list, act_date: str, result: list) -> None:
    """тест для функции, получающей список транзакций с начала месяца по дату, переданную в act_date"""
    assert filter_by_currency_month(get_transactions, act_date) == result


def test_get_top_transactions(get_transactions_2: list) -> None:
    """Тест для функции, которая вычисляет ТОП-5 транзакций по сумме - норма"""
    result = get_top_transactions(get_transactions_2)
    assert result["top_transactions"][0] == {
        "date": "12.01.2018",
        "amount": -87068.0,
        "category": "Путешествия",
        "description": "Оплата отеля",
    }


def test_filtered_by_card_number(get_transactions: list, get_expected: dict) -> None:
    """Тест для функции, которая группирует транзакции по номеру карты - норма"""
    result = filtered_by_card_number(get_transactions)
    assert result[0] == get_expected


def test_get_card_info(get_transactions_1: list) -> None:
    """Тест для функции, формирующей отчет по каждой карте - норма"""
    result = get_card_info(get_transactions_1)
    assert result[0] == {"last_digits": "4556", "total_spent": 88068.0, "cashback": 880.0}


@patch("requests.get")
def test_get_exchange_rate1(mock_get: Any) -> None:
    """Тест для функции, формирующей данные о курсах валют - норма"""
    mock_get.return_value.json.return_value = {"symbol": "USD/RUB", "rate": 81.726, "timestamp": 1746111240}
    assert get_exchange_rate(
        [
            "USD",
        ],
        "RUB",
    ) == [
        {"currency": "USD", "rate": 81.726},
    ]
    mock_get.assert_called_once()


@patch("requests.get")
def test_get_exchange_rate2(mock_get: Any) -> None:
    """Тест для функции, формирующей данные о курсах валют - ошибка API-запроса"""
    mock_get.return_value.json.return_value = {"Error Message": "the parameter apikey is invalid or missing"}
    assert get_exchange_rate(
        [
            "USD",
        ],
        "RUB",
    ) == [
        {"currency": "USD", "rate": "Данные отсутствуют"},
    ]
    mock_get.assert_called_once()


@patch("requests.get")
def test_get_stocks_rates1(mock_get: Any) -> None:
    """Тест для функции, формирующей данные о котировках акций - норма"""
    mock_get.return_value.json.return_value = {"price": "212.44"}
    assert get_stocks_rates(
        [
            "AAPL",
        ]
    ) == [{"stock": "AAPL", "price": "212.44"}]
    mock_get.assert_called_once()


@patch("requests.get")
def test_get_stocks_rates2(mock_get: Any) -> None:
    """Тест для функции, формирующей данные о котировках акций - норма"""
    mock_get.return_value.json.return_value = {"Error Message": "the parameter apikey is invalid or missing"}
    assert get_stocks_rates(
        [
            "AAPL",
        ]
    ) == [{"stock": "AAPL", "price": "Данные отсутствуют"}]
    mock_get.assert_called_once()
