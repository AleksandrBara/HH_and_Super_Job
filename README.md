# Сравниваем зарплату по языкам програмированния.

С помощью этого  скрипта вы можете получить данные статистики по зарплате программистов в Москве. 
Статистика представлена таблицами данных, сгруппированными по языкам программирования.
Скрипт получает данные со следующих сайтов-api:

- [superjob.ru](https://api.superjob.ru/)
- [hh.ru](https://dev.hh.ru/)

## Запуск

- Скачайте код
- Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
- Создайте аккаунт на superjob.ru или используйте существующий
- Зарегистрируйте новое приложение по этой [ссылке](https://api.superjob.ru/info/)
- Запомните свой секретный ключ
- Создать файл `.env` в каталоге скрипта
- Добавьте следующие записи в `.env-file`:
- SJOB_KEY = Ваш секретный ключ
- hh.ru не требует аутентификации
- запустите файл командой:
```
python3 HH_and_Super_Job.py
``` 
## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
