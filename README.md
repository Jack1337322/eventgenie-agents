# EventGenie Agents

AI-сервис агентов на базе GigaChat 2.0 и LangChain для платформы EventGenie.

## 🚀 Технологии

- **Python 3.11**
- **FastAPI**
- **LangChain**
- **GigaChat 2.0**
- **Pydantic**
- **Uvicorn**

## 📋 Требования

- Python 3.11+
- GigaChat API credentials

## ⚙️ Конфигурация

### Получение GigaChat credentials

1. Зарегистрируйтесь на [https://developers.sber.ru/portal/products/gigachat](https://developers.sber.ru/portal/products/gigachat)
2. Создайте приложение и получите Client ID и Client Secret

### Переменные окружения

Создайте файл `.env`:

```bash
GIGACHAT_CLIENT_ID=your_client_id_here
GIGACHAT_CLIENT_SECRET=your_client_secret_here
DATABASE_URL=postgresql://eventgenie:eventgenie_pass@localhost:5433/eventgenie
```

## 🏃 Запуск

### Локальный запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
python -m uvicorn src.main:app --reload --port 8001
```

API будет доступен по адресу http://localhost:8001

### Docker

```bash
docker build -t eventgenie-agents .
docker run -p 8001:8001 \
  -e GIGACHAT_CLIENT_ID=your_client_id \
  -e GIGACHAT_CLIENT_SECRET=your_client_secret \
  eventgenie-agents
```

## 📡 API Endpoints

### Health Check

- `GET /health` - Проверка работоспособности сервиса

### Event Planning

- `POST /generate-plan` - Генерация плана события с помощью GigaChat
  - Анализ типа события, целевой аудитории, количества гостей
  - Создание детального тайм-лайна
  - Генерация списка задач с приоритетами

### Budget Calculation

- `POST /calculate-budget` - Расчет бюджета события с помощью GigaChat
  - Анализ требований события
  - Расчет стоимости по категориям
  - Рекомендации по оптимизации

### Документация API

Swagger UI доступен по адресу: http://localhost:8001/docs

## 🤖 Архитектура агентов

### Maestro Agent
Главный оркестратор, координирующий работу специализированных агентов.

### Planning Agent
Специализируется на создании планов мероприятий:
- Построение тайм-лайна
- Определение ключевых этапов
- Генерация чек-листов

### Finance Agent
Специализируется на финансовом планировании:
- Расчет бюджета по категориям
- Анализ рыночных цен
- Оптимизация расходов

## 📁 Структура проекта

```
src/
├── main.py                 # FastAPI приложение
├── api/
│   └── routes.py          # API endpoints
├── agents/
│   ├── maestro.py         # Orchestrator agent
│   ├── planning_agent.py  # Event planning agent
│   └── finance_agent.py   # Finance agent
├── chains/
│   ├── planning_chain.py  # LangChain для планирования
│   └── budget_chain.py    # LangChain для бюджета
├── llm/
│   └── gigachat_client.py # GigaChat клиент
└── models/
    ├── event.py           # Pydantic модели
    └── budget.py
```

## 🔗 Связанные репозитории

- [EventGenie Backend](https://github.com/Jack1337322/eventgenie-backend)
- [EventGenie Frontend](https://github.com/Jack1337322/eventgenie-frontend)

## 🧪 Тестирование

```bash
# Установка dev зависимостей
pip install -r requirements.txt

# Запуск тестов
pytest
```

## 🔐 Безопасность

- **Не коммитьте** `.env` файл с реальными credentials
- **Используйте** переменные окружения для sensitive данных
- **Ротируйте** API ключи регулярно

## 📊 Мониторинг

Логи доступны через стандартный вывод:

```bash
docker-compose logs -f agents-service
```

## 📄 Лицензия

MIT

## 👥 Команда

Разработано с использованием GigaChat 2.0 и LangChain
