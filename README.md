
Проект содержит Fast API приложение для получения данных о поверке средств измерений (данные взяты из ФГИС Аршин).
REST API позволяет:
  - Получать данные согласно пункту 3.3.7 из описания API ФГИС Аршин https://fgis.gost.ru/fundmetrology/cm/docs/1541318
  - Получать по заданным параметрам статистическую информацию по годам
  - Содержит сервис для отправки данных клиентам о результатах поверки их устройств

Приложение создано согласно Best Practise из документации FastAPI.
Используется пакетный менеджер uv и виртуальные окружения, есть кастомные обработчики ошибок,
логгирование, CORS, JWT аутентификация, каждый endpoint покрыт Unit тестами на pytest.
Для валидации всех входных и выходных данных используется pydantic V3, есть openAPI документация.
Используемые технологии: Python 3.13, PostgreSQL 17, Redis 7.4.1 (с JSON расширением), SQLAlchemy 2.0.36, asyncpg 0.30.0, docker-контейнер на базе Alpine Linux.
* CORS, CSP, сигнатурный анализ отдельно на Angie
