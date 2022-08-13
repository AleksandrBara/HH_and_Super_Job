import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


def get_vacancies(api_url, payload, headers):
    response = requests.get(api_url, payload, headers=headers)
    response.raise_for_status()
    return response.json()


def predict_salary(salary_from, salary_to):
    if salary_from == None and salary_to == None:
        avg_salary = None
    elif salary_from and salary_to:
        avg_salary = float(salary_from + salary_to) / 2
    elif salary_from and not salary_to:
        avg_salary = float(salary_from) * 1.2
    elif salary_to and not salary_from:
        avg_salary = float(salary_to) * 0.8
    return avg_salary


def predict_rub_salary_hh(vacancy):
    if vacancy['salary'] == None:
        salary_from = None
        salary_to = None
    elif vacancy['salary']['currency'] != 'RUR':
        salary_from = None
        salary_to = None
    elif vacancy['salary']['from'] and vacancy['salary']['to']:
        salary_from = vacancy['salary']['from']
        salary_to = vacancy['salary']['to']
    elif vacancy['salary']['from'] and not vacancy['salary']['to']:
        salary_from = vacancy['salary']['from']
        salary_to = None
    elif vacancy['salary']['to'] and not vacancy['salary']['from']:
        salary_from = None
        salary_to = vacancy['salary']['to']
    avg_salary = predict_salary(salary_from, salary_to)
    return avg_salary


def predict_rub_salary_sj(vacancy):
    if vacancy['payment_from'] == None and vacancy['payment_to'] == None:
        salary_from = None
        salary_to = None
    elif vacancy['payment_from'] == 0 and vacancy['payment_to'] == 0:
        salary_from = None
        salary_to = None
    elif vacancy['payment_from'] and vacancy['payment_to']:
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
    elif vacancy['payment_from'] and not vacancy['payment_to']:
        salary_from = vacancy['payment_from']
        salary_to = None
    elif vacancy['payment_to'] and not vacancy['payment_from']:
        salary_from = None
        salary_to = vacancy['payment_to']
    avg_salary = predict_salary(salary_from, salary_to)
    return avg_salary


def get_analytics_from_sjob(languages, sjob_api_url, sjob_headers):
    salary_analytics = {}
    for language in languages:
        salary_in_vacancies = []
        sjob_paload = {
            'keywords': 'Программист {}'.format(language),
            'town': 'Москва',
            'page': '0',
            'count': '50'
        }
        page = 0
        extra_pages = True
        while extra_pages != False:
            sjob_paload['page'] = page
            vacancies = get_vacancies(sjob_api_url, sjob_paload, sjob_headers)
            for vacancy in vacancies['objects']:
                avg_salary = predict_rub_salary_sj(vacancy)
                if avg_salary:
                    salary_in_vacancies.append(avg_salary)
            extra_pages = vacancies['more']
            page += 1
        if len(salary_in_vacancies) != 0:
            average_salary = int(sum(salary_in_vacancies) / len(salary_in_vacancies))
        else:
            average_salary = 0
        vacancies_found = vacancies['total']
        vacancies_processed = len(salary_in_vacancies)
        average_salary_analytics = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }
        salary_analytics.update({language: average_salary_analytics})
    return salary_analytics


def get_analytics_from_hh(languages, hh_api_url, hh_headers):
    salary_analytics = {}
    for language in languages:
        salary_in_vacancies = []
        hh_paload = {
            'text': 'Программист {}'.format(language),
            'period': '30',
            'area': '2',
            'page': '0'
        }
        quantity_of_pages = get_vacancies(hh_api_url, hh_paload, hh_headers)['pages']
        page = 0
        while page < quantity_of_pages:
            hh_paload['page'] = page
            vacancies = get_vacancies(hh_api_url, hh_paload, hh_headers)
            for vacancy in vacancies['items']:
                mean_salary = predict_rub_salary_hh(vacancy)
                if mean_salary:
                    salary_in_vacancies.append(mean_salary)
            page += 1
        if len(salary_in_vacancies) != 0:
            average_salary = int(sum(salary_in_vacancies) / len(salary_in_vacancies))
        else:
            average_salary = 0
        vacancies_found = vacancies['found']
        vacancies_processed = len(salary_in_vacancies)
        average_salary_analytics = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }
        salary_analytics.update({language: average_salary_analytics})
    return salary_analytics


def render_vacancy_table(analytics, title):
    vacancy_table = [
        [
            ' Язык программирования ',
            'Вакансий найдено',
            'Вакансий обработано ',
            'Средняя зарплата'
        ]
    ]
    for key in analytics:
        temp_salary_data = []
        temp_salary_data.append(key)
        temp_salary_data.append(analytics[key]['vacancies_found'])
        temp_salary_data.append(analytics[key]['vacancies_processed'])
        temp_salary_data.append(analytics[key]['average_salary'])
        vacancy_table.append(temp_salary_data)
        rendeted_vacancy_table = AsciiTable(vacancy_table, title)
    return rendeted_vacancy_table


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
    try:
        hh_analytics = get_analytics_from_hh(languages, hh_api_url, hh_headers)
        sjob_analytics = get_analytics_from_sjob(languages, sjob_api_url, sjob_headers)
    except (requests.HTTPError, requests.ConnectionError) as e:
        quit('Получили ошибку: {} '.format(e))
    rendered_vacancy_table_sj = render_vacancy_table(sjob_analytics, 'SuperJob Moscow')
    print(rendered_vacancy_table_sj.table)
    print()
    rendered_vacancy_table_hh = render_vacancy_table(hh_analytics, 'HeadHunter Moscow')
    print(rendered_vacancy_table_hh.table)
