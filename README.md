```markdown
Carousel MVP
```

Backend: **Python + FastAPI + Postgres + MinIO**  
Frontend: **Nuxt 3 (Vue)**  

## 🚀 Как запустить

### Локальный запуск (рекомендуется для разработки)

```bash
# 1. Клонировать репозиторий
git clone git@github.com:ScR1pp1/tech_task.git
cd vibecoding

# 2. Запустить базу данных и MinIO через Docker
docker-compose up -d db minio

# 3. Запустить бэкенд
cd backend
python -m venv venv
source venv/bin/activate  # для macOS/Linux
# или venv\Scripts\activate для Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 4. Запустить фронтенд
cd frontend
npm install
npm run dev

# 5. Открыть в браузере
open http://localhost:3000
```

После запуска:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001 (логин: minioadmin / minioadmin)

## 📋 Примеры запросов (curl)

```bash
# Health check
curl http://localhost:8000/health

# Получить список каруселей
curl -H "X-API-Key: dev-secret-key" http://localhost:8000/carousels

# Создать новую карусель
curl -X POST http://localhost:8000/carousels \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -d '{
    "title": "Instagram growth tips",
    "language": "ru",
    "slides_count": 8,
    "style_hint": "short, bold marketing tips",
    "source_type": "text",
    "source_payload": {"source_text": "5 советов для Instagram: 1. Постите регулярно 2. Используйте Stories 3. Отвечайте на комментарии"}
  }'

# Запустить генерацию слайдов
curl -X POST http://localhost:8000/generations \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -d '{"carousel_id": 1}'

# Получить слайды карусели
curl -H "X-API-Key: dev-secret-key" http://localhost:8000/carousels/1/slides

# Обновить слайд
curl -X PATCH http://localhost:8000/carousels/1/slides/1 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -d '{"title": "Новый заголовок", "body": "Обновленный текст"}'

# Загрузить фоновое изображение
curl -X POST http://localhost:8000/assets/upload \
  -H "X-API-Key: dev-secret-key" \
  -F "file=@image.jpg"

# Оценить стоимость генерации
curl -X POST http://localhost:8000/generations/token-estimate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -d '{
    "source_text": "5 советов для Instagram",
    "slides_count": 8,
    "language": "ru",
    "style_hint": "short, bold"
  }'
```

## 🔧 Что упрощено и почему

| Упрощение | Причина | Как улучшить в проде |
|-----------|---------|----------------------|
| **Экспорт на фронтенде** (html2canvas + JSZip) | Быстрая реализация, не требует серверного рендеринга | Перенести на бэкенд с Playwright/Puppeteer |
| **LLM заглушка** (детерминированная генерация) | MVP не требует реальных затрат на API | Подключить OpenAI/Grok через API ключ |
| **Статический API ключ** | Простота для локальной разработки | Добавить JWT или OAuth |
| **Упрощенная авторизация** | MVP не требует сложной системы пользователей | Добавить регистрацию и разделение по пользователям |
| **Превью в SVG** | Быстрая генерация без Canvas | Генерировать реальные PNG превью |
| **Один Docker volume для разработки** | Hot-reload для быстрой итерации | Разделить на dev/prod конфигурации |

## 📊 Отчёт

### ⏱ Время затраченное на проект

**~22 часа** распределенных следующим образом:

- **Настройка проекта и архитектуры** – 3 часа
- **Backend разработка** (модели, роутеры, БД) – 6 часов
- **Frontend разработка** (страницы, компоненты) – 5 часов
- **Интеграция с MinIO** – 2 часа
- **Дизайн и UI/UX** – 3 часа
- **Отладка и тестирование** – 2 часа
- **Документация и финальные правки** – 1 час

### 🛠 Инструменты вайбкодинга

- **Cursor** – основной редактор с AI (80% кода)
- **GitHub Copilot** – автодополнение (20% кода)

### 🤖 Модель/провайдер

Проект настроен на работу с **любым OpenAI-совместимым API**. В MVP используется заглушка, но при подключении реального API используется:

- **Провайдер**: Groq (для быстрого прототипирования) / OpenAI
- **Модель**: `meta-llama/llama-4-scout-17b-16e-instruct` или `gpt-4o-mini`
- **API Base**: `https://api.groq.com/openai/v1` (для Groq)

### 💰 Примерный расход токенов и стоимость

**Для типичной генерации** (исходный текст 2-3k символов, 8-10 слайдов):

| Параметр | Значение |
|----------|----------|
| Input tokens | ~1,500 - 2,500 |
| Output tokens | ~800 - 1,200 |
| **Total tokens** | **~2,300 - 3,700** |

**Стоимость на разных моделях:**

| Модель | Цена за 1K токенов | Стоимость за генерацию |
|--------|-------------------|------------------------|
| `gpt-4o-mini` | $0.15 / $0.60 (in/out) | **$0.01 - $0.03** |
| `llama-4-scout` (Groq) | Бесплатно (на момент MVP) | **$0.00** |
| `gpt-4o` | $2.50 / $10.00 | **$0.15 - $0.30** |
| `claude-3-haiku` | $0.25 / $1.25 | **$0.02 - $0.05** |

**Итог:** MVP может работать бесплатно (через Groq) или стоить **менее $0.05 за генерацию** при использовании экономичных моделей.

---

## 📁 Структура проекта

```
vibecoding/
├── backend/               # FastAPI бэкенд
│   ├── app/
│   │   ├── routers/       # API endpoints
│   │   ├── models.py      # SQLAlchemy модели
│   │   ├── schemas.py     # Pydantic схемы
│   │   └── services_llm.py # LLM интеграция
│   └── .env               # Конфигурация
├── frontend/              # Nuxt фронтенд
│   ├── pages/             # Страницы
│   ├── components/        # Vue компоненты
│   └── assets/            # Стили
└── docker-compose.yml
```

## ✨ Возможности

- ✅ Создание каруселей из текста
- ✅ Генерация слайдов через AI
- ✅ Редактор с настройками дизайна
- ✅ Экспорт в PNG (ZIP архив)
- ✅ Оценка стоимости токенов
- ✅ Мобильная адаптация
- ✅ Деплой через Docker

## 📝 Лицензия

MIT
```

Этот файл содержит **всё, что требуется**:
1. Инструкцию по запуску
2. Примеры curl запросов
3. Список упрощений и причины
4. Полный отчёт с временем, инструментами и расходами
