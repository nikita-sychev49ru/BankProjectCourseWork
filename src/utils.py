import logging
import os
from datetime import datetime
from typing import Any, Dict

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY_STOCKS")

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "utils_logs.log")
utils_logger = logging.getLogger("services_logger")
utils_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
utils_logger.addHandler(file_handler)


def make_transactions(file_path: str | None = None) -> Any:
    """Функция, считывающая транзакции из xlsx-файла и возвращающая
    их в виде списка словарей python"""
    if not file_path:
        utils_logger.info("поиск файла со списком операций")
        file_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(file_dir, "..", "data", "operations.xlsx")
    try:
        utils_logger.info("формирование списка операций")
        data_frame = pd.read_excel(file_path)
        data_xlsx = data_frame.to_dict(orient="records")
        return data_xlsx
    except FileNotFoundError:
        utils_logger.error("Ошибка! Файл не найден!")
        print("Ошибка! Файл не найден!")
    except Exception:
        utils_logger.error("Ошибка! Данные имеют неверный формат!")
        print("Данные имеют неверный формат!")


def filter_by_currency_month(transactions: list, act_date: str) -> list:
    """Функция отбирает транзакции за текущий месяц"""
    utils_logger.info("отбор транзакций за выбранный период")
    try:
        end_date = datetime.strptime(act_date, "%d.%m.%Y")
        start_date = end_date.replace(day=1)
        filtered_by_month_transactions = []
        for t in transactions:
            t_date = datetime.strptime(t.get("Дата операции", "01.01.2000").split()[0], "%d.%m.%Y")
            if start_date <= t_date <= end_date:
                filtered_by_month_transactions.append(t)
        transactions = filtered_by_month_transactions
        utils_logger.info("список транзакций за выбранный период успешно сформирован")
        return transactions
    except ValueError:
        utils_logger.error("Ошибка! Транзакции за выбранный период отсутствуют")
        return []


def get_top_transactions(transactions: list) -> dict:
    """Функция вычисляет ТОП-5 транзакций по сумме"""
    utils_logger.info("отбор ТОП-5 транзакций за выбранный период")
    transactions_df = pd.DataFrame(transactions)
    top_df = transactions_df.sort_values(by="Сумма платежа", ascending=False, key=lambda x: abs(x)).head(5)
    formatted_transactions = []
    for _, row in top_df.iterrows():
        formatted_transactions.append(
            {
                "date": row["Дата операции"].split()[0],
                "amount": float(row["Сумма платежа"]),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )
    utils_logger.info("ТОП-5 транзакций за выбранный период сформирован")
    return {"top_transactions": formatted_transactions}


def filtered_by_card_number(transactions: list) -> list[Dict]:
    """Функция сортирует транзакции по номеру карты"""
    utils_logger.info("отбор транзакций по номеру карты")
    transactions_df = pd.DataFrame(transactions)
    transactions_df["Номер карты"] = transactions_df["Номер карты"].astype(str).replace("nan", "----")
    transactions_by_cards = [
        {"Номер карты": card, "Транзакции": group.to_dict("records")}
        for card, group in transactions_df.groupby("Номер карты")
    ]
    utils_logger.info("транзакции за выбранный период отсортированы по номеру карты")
    return transactions_by_cards


def get_card_info(transactions: list) -> list:
    """Функция получает выводимую информацию: номер карты,
    сумму расходов за текущий месяц, включая дату, указанную в запросе,
    начисленный кешбэк"""
    utils_logger.info("запрос формирования информации по картам за выбранный период")
    cards = []
    for item in transactions:
        card: dict = {}
        cards.append(card)
        card["last_digits"] = item.get("Номер карты")[1:]
        transactions_df = pd.DataFrame(item.get("Транзакции"))
        payments = float(
            round((transactions_df["Сумма платежа"][transactions_df["Сумма платежа"] < 0].sum()) * (-1), 2)
        )
        cashback = float(round(transactions_df["Кэшбэк"].replace(pd.NA, 0).sum(), 2))

        card["total_spent"] = float(payments)
        card["cashback"] = float(cashback)
    utils_logger.info("информации по картам за выбранный период успешно сформирована")
    return cards


def get_exchange_rate(currency_op: list, currency_main: str) -> list:
    """Функция запрашивает курс заданной валюты к валюте счета пользователя"""
    utils_logger.info("запрос информации по курсам валют")
    currency_rates = []
    url = "https://api.twelvedata.com/exchange_rate"
    for item in currency_op:
        params = {"symbol": f"{item}/{currency_main}", "apikey": API_KEY}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        currency_rate = {}
        currency_rate["currency"] = item
        currency_rate["rate"] = data.get("rate", "Данные отсутствуют")
        currency_rates.append(currency_rate)
    utils_logger.info("доступная информация по курсам валют получена")
    return currency_rates


def get_stocks_rates(stocks: list) -> list:
    """Функция запрашивает актуальный курс выбранных акций из индекса S&P500"""
    utils_logger.info("запрос информации по котировкам акций")
    stocks_rates = []
    url = "https://api.twelvedata.com/price"
    for item in stocks:
        stock_info = {}
        stock_info["stock"] = item
        params = {"symbol": item, "apikey": API_KEY}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        stock_info["price"] = data.get("price", "Данные отсутствуют")
        if stock_info.get("price") != "Данные отсутствуют":
            stock_info["price"] = str(round(float(stock_info["price"]), 2))
        stocks_rates.append(stock_info)
    utils_logger.info("доступная информация по котировкам акций получена")
    return stocks_rates
