# EventGenie Agents Service — CLAUDE.md

## Обзор

EventGenie Agents Service — это FastAPI сервис с многоагентной AI‑логикой на базе LangChain и GigaChat. Выполняет:

- Генерацию детального плана события (Planning Agent)
- Расчёт бюджета и рекомендаций (Finance Agent)
- Оркестрацию и маршрутизацию запросов (Maestro Agent)

---

## 📋 Технологический стек

- **Language:** Python 3.11+
- **Framework:** FastAPI 0.109.0
- **ASGI Server:** Uvicorn 0.27.0
- **LLM Integration:** GigaChat API (официальный SDK)
- **Orchestration:** LangChain 0.1.4
- **Database:** PostgreSQL + asyncpg 0.29.0 + SQLAlchemy 2.0.25
- **Validation:** Pydantic 2.5.3
- **HTTP Client:** httpx 0.26.0

---

## 📁 Структура проекта

```
agents/
├── src/
│   ├── main.py                      # FastAPI приложение
│   ├── api/
│   │   └── routes.py                # REST API endpoints
│   ├── agents/
│   │   ├── planning_agent.py        # Planning Agent
│   │   ├── finance_agent.py         # Finance Agent
│   │   └── maestro.py               # Maestro Agent (оркестрация)
│   ├── chains/
│   │   ├── planning_chain.py        # LangChain для планирования
│   │   └── budget_chain.py          # LangChain для бюджета
│   ├── llm/
│   │   └── gigachat_client.py       # Клиент GigaChat API
│   └── models/
│       ├── event.py                 # Pydantic модели событий
│       └── budget.py                # Pydantic модели бюджетов
├── requirements.txt
└── Dockerfile
```

---

## 🔌 REST API Endpoints

Все endpoints под префиксом `/api/v1`

### Planning Agent

```http
POST /api/v1/agents/planning/generate
```

**Request (EventPlanRequest):**

```json
{
  "event_name": "Свадьба Ивана и Марии",
  "event_type": "wedding",
  "event_date": "2025-04-15T18:00:00",
  "location": "Москва, загородный клуб",
  "expected_guests": 150,
  "budget": 1000000.0,
  "target_audience": "Молодые пары 25-35 лет",
  "format": "hybrid"
}
```

**Response:**

```json
{
  "timeline": {
    "timeline_phases": [
      {
        "time": "18:00",
        "activity": "Регистрация гостей и встреча"
      },
      {
        "time": "18:30",
        "activity": "Фуршет и живая музыка"
      },
      {
        "time": "19:30",
        "activity": "Ужин и торжественные речи"
      }
    ]
  },
  "tasks": {
    "tasks": [
      {
        "title": "Выбор площадки",
        "description": "Забронировать загородный клуб",
        "deadline_days": 60,
        "priority": "CRITICAL"
      },
      {
        "title": "Пригласительные",
        "description": "Заказать печать приглашений",
        "deadline_days": 45,
        "priority": "HIGH"
      }
    ]
  }
}
```

### Finance Agent

```http
POST /api/v1/agents/finance/calculate
```

**Request (BudgetCalculationRequest):**

```json
{
  "event_name": "Свадьба Ивана и Марии",
  "event_type": "wedding",
  "event_date": "2025-04-15",
  "location": "Москва",
  "expected_guests": 150,
  "budget_limit": 1000000.0
}
```

**Response:**

```json
{
  "items": [
    {
      "category": "Площадка",
      "planned_amount": 150000.0,
      "description": "Аренда загородного клуба"
    },
    {
      "category": "Кейтеринг",
      "planned_amount": 450000.0,
      "description": "Полный пакет еды и напитков для 150 человек"
    },
    {
      "category": "Развлечения",
      "planned_amount": 200000.0,
      "description": "DJ, живая музыка, фотограф, видеограф"
    },
    {
      "category": "Декор",
      "planned_amount": 100000.0,
      "description": "Цветы, светоустановка, оформление"
    },
    {
      "category": "Прочее",
      "planned_amount": 100000.0,
      "description": "Приглашения, подарки гостям, транспорт"
    }
  ],
  "total_amount": 1000000.0,
  "analysis": "Распределение бюджета оптимально для мероприятия такого класса...",
  "recommendations": "Рекомендуется выделить больше на кейтеринг..."
}
```

### Maestro Agent

```http
POST /api/v1/agents/maestro/process
```

**Request (MaestroRequest):**

```json
{
  "user_id": "user-123",
  "message": "Создай план свадьбы на 150 человек",
  "context": {
    "previous_events": []
  }
}
```

**Response:** Агрегированный результат работы одного или нескольких агентов

---

## 🤖 AI Агенты

### 1. Planning Agent (`agents/planning_agent.py`)

**Ответственность:**

- Генерирует полный план события
- Создаёт timeline с фазами и активностями
- Генерирует список задач с приоритетами и дедлайнами

**Метод:**

```python
async def generate_event_plan(event_data: dict) -> dict
```

**Использует:** `PlanningChain` из `chains/planning_chain.py`

**Возвращает структуру:** timeline phases + list of tasks

### 2. Finance Agent (`agents/finance_agent.py`)

**Ответственность:**

- Строит детальную структуру бюджета события
- Разбивает по категориям расходов (Площадка, Кейтеринг, Развлечения и т.д.)
- Генерирует анализ и рекомендации по оптимизации

**Метод:**

```python
async def calculate_budget(event_data: dict) -> dict
```

**Использует:** `BudgetChain` из `chains/budget_chain.py`

**Возвращает:** items, total_amount, analysis, recommendations

### 3. Maestro Agent (`agents/maestro.py`)

**Ответственность:**

- Определяет, какие агенты вызвать на основе сообщения
- Парсит намерение пользователя
- Маршрутизирует запросы к нужным агентам
- Объединяет результаты в единую структуру

**Метод:**

```python
async def process_request(user_id: str, message: str, context: dict | None = None) -> dict
```

---

## 🔗 LangChain Chains

### PlanningChain (`chains/planning_chain.py`)

**Процесс:**

1. Формирует промпт с параметрами события
2. Вызывает GigaChat через `GigaChatClient`
3. Парсит JSON ответ
4. Валидирует структуру (наличие phases и tasks)
5. Возвращает готовый объект

**Особенности:**

- Использует prompt template специальную для планирования
- Поддерживает JSON режим LLM
- Обработка ошибок и retry логика

### BudgetChain (`chains/budget_chain.py`)

**Процесс:**

1. Формирует промпт для расчёта бюджета
2. Получает от LLM список статей расходов в JSON
3. Суммирует `planned_amount` → `total_amount`
4. Генерирует текст анализа и рекомендации

**Особенности:**

- Структурированный JSON ответ от LLM
- Гарантированное наличие основных категорий
- Валидация и расчёты

---

## 🎯 GigaChat Integration (`llm/gigachat_client.py`)

**Клиент для работы с GigaChat API:**

### Инициализация

```python
from llm.gigachat_client import GigaChatClient

client = GigaChatClient(
    client_id=os.getenv("GIGACHAT_CLIENT_ID"),
    client_secret=os.getenv("GIGACHAT_CLIENT_SECRET"),
    model="GigaChat"
)
```

### Методы

```python
async def generate(prompt: str, temperature: float = 0.7) -> str
    # Генерирует текстовый ответ

async def generate_json(prompt: str, temperature: float = 0.3) -> dict
    # Генерирует JSON структурированный ответ
```

### Особенности

- Асинхронные вызовы через httpx
- Обработка ошибок API и таймаутов
- Логирование запросов и ответов
- Поддержка JSON режима для структурированных данных
- Повторные попытки при сбое

---

## ⚙️ Конфигурация и окружение

### Переменные окружения

```bash
GIGACHAT_CLIENT_ID=your_client_id
GIGACHAT_CLIENT_SECRET=your_client_secret
GIGACHAT_MODEL=GigaChat
DATABASE_URL=postgresql://eventgenie:eventgenie_pass@postgres:5432/eventgenie
```

### FastAPI Настройки

- **CORS middleware** для всех origins (development)
- **Swagger UI** документация на `/docs`
- **ReDoc** документация на `/redoc`
- **Health check** endpoint на `/health`

---

## 🔧 Особенности реализации

### Асинхронность

- Все API‑хендлеры — `async def`
- Все вызовы к LLM через `await`
- httpx для асинхронных HTTP запросов
- asyncpg/SQLAlchemy для асинхронной работы с БД

### Валидация

- Pydantic 2.x модели для входящих запросов
- Автоматическая валидация в FastAPI
- Type hints для всех методов

### Обработка ошибок и логирование

- `HTTPException` для API ошибок
- Структурированное логирование входных данных
- Логирование результатов и времени выполнения

---

## 🚀 Запуск и разработка

### Установка зависимостей

```bash
cd agents
pip install -r requirements.txt
```

### Запуск приложения

```bash
# Способ 1: Прямой запуск
cd src
python main.py

# Способ 2: Через uvicorn
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Приложение будет доступно на `http://localhost:8001`

### Документация API

- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

---

## 📊 Поток данных в системе

### Генерация плана события

```
Backend (POST /api/v1/event-plans/generate/{eventId})
    ↓
AgentIntegrationService
    ↓
Agents Service (POST /api/v1/agents/planning/generate)
    ↓
PlanningAgent.generate_event_plan()
    ↓
PlanningChain
    ↓
GigaChatClient.generate_json()
    ↓
GigaChat API
    ↓
LLM Response (JSON)
    ↓
Парсинг и валидация
    ↓
Backend сохраняет в PostgreSQL
    ↓
Frontend отображает результат
```

### Расчёт бюджета

```
Backend (POST /api/v1/budgets/calculate/{eventId})
    ↓
AgentIntegrationService
    ↓
Agents Service (POST /api/v1/agents/finance/calculate)
    ↓
FinanceAgent.calculate_budget()
    ↓
BudgetChain
    ↓
GigaChatClient.generate_json()
    ↓
GigaChat API
    ↓
LLM Response (JSON с items и total_amount)
    ↓
Расчёты и генерация анализа
    ↓
Backend сохраняет в PostgreSQL
    ↓
Frontend отображает результат
```

---

## 🔗 Связанные репозитории

- **Frontend:** Jack1337322/eventgenie-frontend
- **Backend:** Jack1337322/eventgenie-backend

---

**Последнее обновление:** Декабрь 2025
