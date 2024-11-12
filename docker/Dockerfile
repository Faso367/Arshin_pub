FROM python:3.13-alpine

RUN apk update && \
    apk add --no-cache gcc g++ libffi-dev make musl-dev postgresql-dev \
    linux-headers openssl-dev cargo

WORKDIR /project/app

# Копируем файл зависимостей pyproject.toml в контейнер
COPY ./app/pyproject.toml ./

# Зависимости установятся напрямую в контейнер (не в виртуальное окружение)
RUN pip install --upgrade pip && \
    pip install uv && \
    uv pip install -r pyproject.toml --all-extras --system


WORKDIR /project
# Копируем весь код приложения из локальной папки app в контейнер
COPY ./app /app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--lifespan", "on"]
