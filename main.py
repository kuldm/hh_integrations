import time
from dataclasses import dataclass, asdict
from functools import wraps

import requests
import json

url = "https://api.hh.ru/vacancies"


@dataclass
class VacanciesData:
    name: str
    url: str
    salary: dict | None = None


def retry(retries: int, delay: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Ошибка: {e}, повтор через {delay}с...")
                    time.sleep(delay)
            raise Exception("Все попытки исчерпаны")

        return wrapper

    return decorator


@retry(retries=3, delay=2)
def fetch_hh_vacancies(url: str, page: int = 0):
    query_params = {
        "text": "fastapi",
        "per_page": 100,
        "page": page,
    }
    resp = requests.get(url, query_params, timeout=10)
    if resp.status_code != 200:
        print("Запрос упал с ошибкой", resp.text)
    print(f"Успешно получены вакансии {page=}")
    result = resp.json()
    return result


def parse_vacancies(data: dict) -> list[VacanciesData]:
    current_info = []
    for item in data["items"]:
        current_info.append(
            VacanciesData(
                name=item["name"], salary=item["salary"], url=item["alternate_url"]
            )
        )
    return current_info


def fetch_all_hh_vacancies(url: str):
    page = 0
    all_items: list[VacanciesData] = []
    while page < 20:
        data = fetch_hh_vacancies(url, page)
        items = parse_vacancies(data)
        if not items:
            break
        all_items.extend(items)
        page += 1
        time.sleep(0.2)

    payload = [asdict(v) for v in all_items]
    with open("vacancies.json", "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def main():
    fetch_all_hh_vacancies(url)


if __name__ == "__main__":
    main()
