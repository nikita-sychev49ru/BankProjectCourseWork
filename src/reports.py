import json
import logging
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd


log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "reports_logs.log")
reports_logger = logging.getLogger("services_logger")
reports_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
reports_logger.addHandler(file_handler)


def report_log(filename: str = "report.json") -> Any:
    """Декоратор, который записывает результаты формирования отчетов в файл.
    Можно передать в аргумент декоратора название для файла с отчетами, по умолчанию -
    report.txt"""

    def decorator1(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            reports_logger.info("запрос на создание отчета о транзакциях по категории")
            result = func(*args, **kwargs)
            if isinstance(result, pd.DataFrame):
                dir_path = os.path.dirname(os.path.abspath(__file__))
                reports_data_dir = os.path.join(dir_path, "..", "reports_data")
                os.makedirs(reports_data_dir, exist_ok=True)
                file_path = os.path.join(reports_data_dir, filename)
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                        reports_logger.info(f"запись отчета о транзакциях по категории в файл {filename}")
                        json.dump(result.to_dict(orient="records"), file, ensure_ascii=False, indent=4)
                    reports_logger.info("отчет о транзакциях по категории успешно сохранен")
                except Exception as e:
                    reports_logger.error("ошибка при сохранении отчета")
                    print(f"Ошибка при сохранении отчета: {e}")
            return result

        return wrapper

    return decorator1


@report_log()
def spending_by_category(transactions_df: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция получает список транзакций (DF), категорию и дату (по умолчанию - текущую)
    и возвращает траты по заданной категории за последние три месяца (от переданной даты)."""
    reports_logger.info(f"получение данных о периоде для отчета о транзакциях по категории {category}")

    if date:
        end_date = None
        while not end_date:
            try:
                end_date = pd.to_datetime(date, dayfirst=True)
            except ValueError as e:
                reports_logger.error(f"Ошибка в формате даты: {date}. Ошибка: {str(e)}")
                print(f"Неверный формат даты - {date}! Используйте формат ДД.ММ.ГГГГ")
                date = input("Введите дату для формирования отчета в формате 'ДД.ММ.ГГГГ': ")

    else:
        end_date = pd.to_datetime(datetime.now())

    start_date = end_date - pd.DateOffset(months=3)
    transactions_df["Дата операции"] = pd.to_datetime(transactions_df["Дата операции"], dayfirst=True)
    reports_logger.info(f"формирование отчета о транзакциях по категории {category}")
    filtered_transactions_df = transactions_df[
        (transactions_df["Дата операции"] >= start_date)
        & (transactions_df["Дата операции"] <= end_date)
        & (transactions_df["Категория"] == category)
    ]
    filtered_transactions_df = filtered_transactions_df.copy()
    filtered_transactions_df["Дата операции"] = filtered_transactions_df["Дата операции"].dt.strftime(
        "%d.%m.%Y %H:%M:%S"
    )

    return filtered_transactions_df