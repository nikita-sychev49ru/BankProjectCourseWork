import json
import logging
import os
import re
from typing import Optional

from src.utils import make_transactions

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "services_logs.log")
services_logger = logging.getLogger("services_logger")
services_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
services_logger.addHandler(file_handler)


def search_by_target(transactions: list, input_target: str) -> str:
    """Функция возвращает JSON со всеми транзакциями,
    содержащими в описании или категории строку, заданную пользователем"""
    services_logger.info("получение списка транзакций и ключевого слова для поиска")

    target = re.compile(rf"(?:^|\s){input_target}(?:$|\s)", flags=re.IGNORECASE)
    print(target)
    matched_transactions = []
    for transaction in transactions:
        description = transaction.get("Описание", "")
        category = transaction.get("Категория", "")
        if re.search(target, str(description)) or re.search(target, str(category)):
            matched_transactions.append(transaction)
    if len(matched_transactions) != 0:
        services_logger.info("поиск произведен успешно")
        return json.dumps(matched_transactions, ensure_ascii=False)
    else:
        services_logger.warning("поиск не дал результатов")
        return json.dumps({"Результаты поиска": "Ничего не нашлось"}, ensure_ascii=False)


def search_by_phones(transactions: list) -> str:
    """Функция возвращает JSON со всеми транзакциями,
    содержащими в описании мобильные номера"""
    services_logger.info("получение списка транзакций")
    if not transactions:
        transactions = make_transactions()
    phones_transactions = []
    for transaction in transactions:
        if re.search(
            r"(?:^|\s)(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?:$|\s)",
            transaction.get("Описание", ""),
        ):
            phones_transactions.append(transaction)
    services_logger.info("формирование ответа")
    if len(phones_transactions) != 0:
        services_logger.info("поиск произведен успешно")
        return json.dumps(phones_transactions, ensure_ascii=False)
    else:
        services_logger.warning("поиск не дал результатов")
        return json.dumps({"Результаты поиска": "Ничего не нашлось"}, ensure_ascii=False)

print(search_by_phones(make_transactions()))