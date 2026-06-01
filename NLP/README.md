# Resume Summary Generator — FastAPI Service

Этот сервис предназначен для генерации краткого summary в верхней части резюме студента. В дальнейшем эта сгенерированная сводка объединяется с остальными блоками для создания полноценного итогового резюме.

Обёртка над pipeline из `ML.ipynb` в виде HTTP-сервиса.

## Запуск


### Docker Compose

```bash
cp ../.env.example ../.env   # укажите свой GROQ_API
docker compose up --build
```

Сервис будет доступен на `http://127.0.0.1:8000`.

## Переменные окружения

Убедитесь, что задан один из ключей:
- `GROQ_API`
- `GROQ_API_KEY`

При локальном запуске сервис автоматически подгружает `.env` из корня проекта (`../.env`).  
При запуске через Docker Compose `.env` монтируется из корня репозитория (`env_file: ../.env`).

## Endpoints

| Method | Path | Описание |
|--------|------|----------|
| GET | `/health` | Health-check |
| POST | `/generate-summary` | Генерация summary по данным кандидата |

## Пример запроса

```bash
curl -X POST http://127.0.0.1:8000/generate-summary \
  -H "Content-Type: application/json" \
  -d '{
    "educationYear": "2 курс бакалавриата",
    "specialization": "Computer Science",
    "targetRole": "Junior Ml Developer",
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "projects": [
      {"name": "Resume Generator", "description": "Сервис для генерации резюме через LLM"}
    ],
    "personalTraits": ["быстро учусь", "ответственный"],
    "language": "ru"
  }'
```

### Output
```json
{
  "field": "summary",
  "text": "Я - перспективный студент-разработчик, нацеленный на карьеру Junior Ml Developer. На втором курсе бакалавриата по Computer Science, я уже приобрел опыт в работе с технологиями машинного обучения и глубокого обучения, в том числе с использованием Python, FastAPI, PostgreSQL, Docker и Git. Мне особенно интересен опыт в проектах, связанных с машинным обучением и анализом данных, таких как время серии модели для прогноза лучших рекламных каналов, с которым я добился успеха в хакатонах METU и IT-Fest."
}
```

## OpenAPI / Docs

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
