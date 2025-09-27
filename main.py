import pandas as pd

from src.reports import spending_by_category
from src.services import search_by_phones, search_by_target
from src.utils import make_transactions
from src.views import main_views


def main() -> None:
    """Функция определяет главную логику проекта: в зависимости от ввода пользователя
    обращается к тем или иным модулям и возвращает данные в формате JSON"""
    # обработка и формирование информации для Главной страницы
    print(main_views())

    # запуск функционала поиска по ключевому слову
    search_by_target_check = bool(
        int(
            input(
                """Хотите воспользоваться поиском по ключевому слову?
                Нажмите
                1 - если ДА
                0 - если НЕТ
                => """
            )
        )
    )
    if search_by_target_check:
        transactions: list = make_transactions()
        input_target: str = input("Введите значение для поиска: ").strip()

        search_by_target_result = search_by_target(transactions, input_target)
        print("Результаты поиска по заданным словам:")
        print(search_by_target_result)

    # запуск функционала поиска по номера телефона
    search_by_phones_check = bool(
        int(
            input(
                """Хотите воспользоваться поиском по номерам телефонов?
                Нажмите
                1 - если ДА
                0 - если НЕТ
                => """
            )
        )
    )
    if search_by_phones_check:
        transactions1: list = make_transactions()
        search_by_phones_result = search_by_phones(transactions1)
        print("Результаты поиска по номерам телефонов:")
        print(search_by_phones_result)

    # запуск функционала по формированию отчета о тратах по выбранной категории
    spending_by_category_check = bool(
        int(
            input(
                """Хотите получить отчет о тратах по категории?
    Нажмите
    1 - если ДА
    0 - если НЕТ
    => """
            )
        )
    )
    if spending_by_category_check:
        transactions_df = pd.DataFrame(make_transactions())
        category = input("Введите категорию для формирования отчета: ")
        date = input("Введите дату для формирования отчета в формате 'ДД.ММ.ГГГГ': ")
        spending_by_category_result = spending_by_category(transactions_df, category, date)
        total_amount = round(spending_by_category_result["Сумма платежа"].sum(), 2)
        print(
            f"""Общая сумма расходов по категории '{category}' - {total_amount}
Подробнее со списком транзакций можно ознакомиться в файле reports_data/report.json"""
        )


if __name__ == "__main__":
    main()