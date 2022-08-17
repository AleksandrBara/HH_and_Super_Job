import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


def get_vacancies(api_url, payload, headers):
    response = requests.get(api_url, payload, headers=headers)
    response.raise_for_status()
    return response.json()


def predict_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        avg_salary = None
    elif salary_from and salary_to:
        avg_salary = float(salary_from + salary_to) / 2
    elif salary_from and not salary_to:
        avg_salary = float(salary_from) * 1.2
    elif salary_to and not salary_from:
        avg_salary = float(salary_to) * 0.8
    return avg_salary


def predict_rub_salary_for_hh(vacancy):
    salary_from = None
    salary_to = None
    if not vacancy['salary']:
        return salary_from, salary_to
    if vacancy['salary']['currency'] != 'RUR':
        return salary_from, salary_to
    if vacancy['salary']['from']:
        salary_from = vacancy['salary']['from']
    if vacancy['salary']['to']:
        salary_to = vacancy['salary']['to']
    return salary_from, salary_to


def predict_rub_salary_for_sj(vacancy):
    salary_from = None
    salary_to = None
    if vacancy['payment_from']:
        salary_from = vacancy['payment_from']
    if vacancy['payment_to']:
        salary_to = vacancy['payment_to']
    return salary_from, salary_to


def get_analytics_from_sjob(languages, sjob_api_url, sjob_headers):
    salary_analytics = {}
    for language in languages:
        salaries = []
        sjob_payload = {
            'keywords': 'Программист {}'.format(language),
            'town': 'Москва',
            'page': '{}'.format(first_page_number),
            'count': '{}'.format(number_of_results_per_page)
        }
        page = 0
        extra_pages = True
        while extra_pages:
            sjob_payload['page'] = page
            vacancies = get_vacancies(sjob_api_url, sjob_payload, sjob_headers)
            for vacancy in vacancies['objects']:
                salary_from, salary_to = predict_rub_salary_for_sj(vacancy)
                avg_salary = predict_salary(salary_from, salary_to)
                if avg_salary:
                    salaries.append(avg_salary)
            extra_pages = vacancies['more']
            page += 1
        if not salaries:
            average_salary = 0
        else:
            average_salary = int(sum(salaries) / len(salaries))
        vacancies_found = vacancies['total']
        vacancies_processed = len(salaries)
        average_salary_analytics = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }
        salary_analytics[language] = average_salary_analytics
    return salary_analytics


def get_analytics_from_hh(languages, hh_api_url, hh_headers):
    salary_analytics = {}
    for language in languages:
        salaries = []
        hh_payload = {
            'text': 'Программист {}'.format(language),
            'period': '{}'.format(period_of_searching),
            'area': '{}'.format(city_name),
            'page': '{}'.format(first_page_number)
        }
        pages_number = 1
        page = 0
        while page < pages_number:
            hh_payload['page'] = page
            vacancies = get_vacancies(hh_api_url, hh_payload, hh_headers)
            for vacancy in vacancies['items']:
                salary_from, salary_to = predict_rub_salary_for_hh(vacancy)
                avg_salary = predict_salary(salary_from, salary_to)
                if avg_salary:
                    salaries.append(avg_salary)
            page += 1
            pages_number = vacancies['pages']
        if not salaries:
            average_salary = 0
        else:
            average_salary = int(sum(salaries) / len(salaries))
        vacancies_found = vacancies['found']
        vacancies_processed = len(salaries)
        average_salary_analytics = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }
        salary_analytics[language] = average_salary_analytics
    return salary_analytics


def make_table(analytics, title):
    vacancy_table = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано ',
            'Средняя зарплата'
        ]
    ]
    for language, language_analityc in analytics.items():
        table_elements = []
        table_elements.append(language)
        table_elements.extend(language_analityc.values())
        vacancy_table.append(table_elements)
        vacancies_table = AsciiTable(vacancy_table, title)
    return vacancies_table


if __name__ == '__main__':
    load_dotenv()
    sjob_key = os.getenv("SJOB_KEY")
    sjob_api_url = 'https://api.superjob.ru/2.0/vacancies'
    sjob_headers = {'X-Api-App-Id': sjob_key}
    hh_api_url = 'https://api.hh.ru/vacancies'
    hh_headers = {}
    languages = [
        'go',
        'C',
        'CSS',
        'Scala',
        'PHP',
        'Ruby',
        'Python',
        'Java',
        'JavaScript'
    ]
    first_page_number = 0
    city_name = 2
    period_of_searching = 30
    number_of_results_per_page = 50
    try:
        hh_analytics = get_analytics_from_hh(languages, hh_api_url, hh_headers)
        sjob_analytics = get_analytics_from_sjob(languages, sjob_api_url, sjob_headers)
    except (requests.HTTPError, requests.ConnectionError) as e:
        quit('Получили ошибку: {} '.format(e))
    sjob_vacancies_table = make_table(sjob_analytics, 'SuperJob Moscow')
    print(sjob_vacancies_table.table)
    print()
    hh_vacancies_table = make_table(hh_analytics, 'HeadHunter Moscow')
    print(hh_vacancies_table.table)
