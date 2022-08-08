import requests

paload = {
'text':'программист python',
'period':'100',
'area':'1'
}

try:
    response = requests.get('https://api.hh.ru/vacancies', paload)
    response.raise_for_status()
    print(response.json()['found'])
except (requests.HTTPError, requests.ConnectionError) as e:
    print('Получили ошибку: {} '.format(e))