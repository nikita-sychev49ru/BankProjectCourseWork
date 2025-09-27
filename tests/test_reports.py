import os
import tempfile
from unittest.mock import patch
import pandas as pd
import pytest

from src.reports import report_log, spending_by_category


def test_report_log1() -> None:
    """тест для декоратора, записывающего результаты основной функции в json-файл - норма"""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        filename = temp_file.name
    try:

        @report_log(filename=filename)
        def square_cube_nums() -> pd.DataFrame:
            new_list = []
            for x in range(1, 3):
                new_list.append({"square": x**2, "cube": x**3})
            return pd.DataFrame(new_list)

        square_cube_nums()
        with open(filename, "r") as file:
            result = file.read().strip()

            assert "square" in result
            assert "cube" in result

    finally:
        if os.path.exists(filename):
            os.remove(filename)


def test_report_log2() -> None:
    """тест для декоратора, записывающего результаты основной функции в json-файл -
    передан пустой dataframe"""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        filename = temp_file.name
    try:

        @report_log(filename=filename)
        def get_empty_df() -> pd.DataFrame:
            new_list: list = []
            return pd.DataFrame(new_list)

        get_empty_df()
        with open(filename, "r") as file:
            result = file.read().strip()
            assert "" in result

    finally:
        if os.path.exists(filename):
            os.remove(filename)


def test_report_log3(capsys: pytest.CaptureFixture[str]) -> None:
    """тест для декоратора, записывающего результаты основной функции в json-файл -
    ошибка при сохранении"""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        filename = temp_file.name
    try:

        @report_log(filename=filename)
        def get_date_df(date: str = "20.02.2020") -> pd.DataFrame:
            new_list = []
            date = pd.to_datetime(date, dayfirst=True)
            new_list.append({"date": date})
            return pd.DataFrame(new_list)

        get_date_df()
        with open(filename, "r") as file:
            file.read()
            captured = capsys.readouterr()
            assert "Ошибка при сохранении отчета" in captured.out

    finally:
        if os.path.exists(filename):
            os.remove(filename)


@pytest.mark.parametrize("date_str", ["31.03.2023", "31/03/2023", "2023-03-31"])
def test_spending_by_category1(date_str: str) -> None:
    """Тест для фильтрации данных по категории - варианты нормы"""
    test_data = pd.DataFrame({"Дата операции": ["01.03.2023 12:00:00"], "Категория": ["Еда"], "Сумма": [1000]})
    result = spending_by_category(test_data, "Еда", date_str)
    assert len(result) == 1


def test_spending_by_category2(capsys) -> None:
    """Тест для фильтрации данных по категории - ошибка в формате даты"""
    with patch('builtins.input', return_value="01.03.2023"):
        test_data = pd.DataFrame({"Дата операции": ["01.03.2023 12:00:00"], "Категория": ["Еда"], "Сумма": [1000]})
        spending_by_category(test_data, "Еда", "00.01.0001")
        captured = capsys.readouterr()
        assert "Неверный формат даты - 00.01.0001! Используйте формат ДД.ММ.ГГГГ"


@pytest.mark.parametrize("date, category", [("31.03.2024", "Еда"), ("31/03/2023", "Транспорт")])
def test_spending_by_category3(date: str, category: str) -> None:
    """Тест для фильтрации данных по категории - данные по заданной категории
    в заданном периоде отсутствуют - возвращает пустой DF"""
    test_data = pd.DataFrame({"Дата операции": ["01.03.2023 12:00:00"], "Категория": ["Еда"], "Сумма": [1000]})
    result = spending_by_category(test_data, category, date)
    assert len(result) == 0