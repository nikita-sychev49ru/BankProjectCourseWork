import json
from unittest.mock import patch

import pytest

from src.services import search_by_phones, search_by_target


@pytest.mark.parametrize(
    "transactions, expected",
    [
        (
            [{"Описание": "Колхоз", "Категория": 101}, {"Описание": "Перевод", "Категория": "Колхоз"}],
            [{"Описание": "Колхоз", "Категория": 101}, {"Описание": "Перевод", "Категория": "Колхоз"}],
        ),
        (
            [{"Описание": "КОЛХОЗ", "Категория": "ДОСТАВКА"}, {"Описание": "Перевод", "Категория": "Колхо"}],
            [{"Описание": "КОЛХОЗ", "Категория": "ДОСТАВКА"}],
        ),
        (
            [
                {
                    "Описание": "",
                },
                {
                    "iD": "Колхоз",
                },
            ],
            {"Результаты поиска": "Ничего не нашлось"},
        ),
    ],
)
def test_search_by_target(transactions: list, expected: list) -> None:
    """тесты для поиска под ключевому слову"""
    with (patch("src.services.make_transactions", return_value=transactions),):
        result = json.loads(search_by_target(transactions, "Колхоз"))
        assert result == expected


@pytest.mark.parametrize(
    "transactions, expected",
    [
        (
            [{"Описание": "+7-912-222-11-33"}, {"Описание": "89995557700"}],
            [{"Описание": "+7-912-222-11-33"}, {"Описание": "89995557700"}],
        ),
        (
            [{"Описание": "8-912-222-11-33"}, {"Описание": "899955577000"}],
            [
                {"Описание": "8-912-222-11-33"},
            ],
        ),
        ([{"Описание": ""}, {"iD": "89995557700"}], {"Результаты поиска": "Ничего не нашлось"}),
    ],
)
def test_search_by_phones(transactions: list, expected: list) -> None:
    """тесты для поиска транзакций с номерами телефонов в описании"""
    with patch("src.services.make_transactions", side_effect=transactions):
        result = json.loads(search_by_phones(transactions))
        assert result == expected
