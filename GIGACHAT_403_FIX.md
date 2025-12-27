# Решение проблемы 403 Forbidden с GigaChat API

## Причины ошибки 403

Ошибка 403 Forbidden при вызове GigaChat API обычно означает проблемы с аутентификацией:

1. **Неверные credentials** - неправильный `GIGACHAT_CLIENT_ID` или `GIGACHAT_CLIENT_SECRET`
2. **Неправильный scope** - неверный scope для вашего типа аккаунта
3. **Истекший токен** - токен доступа истек
4. **Недостаточные права** - у credentials нет прав на использование API

## Решения

### 1. Проверьте credentials

Убедитесь, что переменные окружения установлены правильно:

```bash
echo $GIGACHAT_CLIENT_ID
echo $GIGACHAT_CLIENT_SECRET
```

### 2. Проверьте scope

В зависимости от типа аккаунта GigaChat, используйте правильный scope:

- **Личный аккаунт**: `GIGACHAT_API_PERS` (по умолчанию)
- **Корпоративный аккаунт**: `GIGACHAT_API_CORP`

Можно задать через переменную окружения:
```bash
export GIGACHAT_SCOPE=GIGACHAT_API_PERS
```

### 3. Получите новые credentials

1. Перейдите на https://developers.sber.ru/portal/products/gigachat
2. Войдите в свой аккаунт
3. Создайте новое приложение или проверьте существующее
4. Скопируйте `Client ID` и `Client Secret`

### 4. Используйте прямой токен (альтернатива)

Если у вас есть access token, можно использовать его напрямую:

```bash
export GIGACHAT_ACCESS_TOKEN=your_access_token_here
```

### 5. Проверьте права доступа

Убедитесь, что ваше приложение в портале Sber имеет права на:
- Использование GigaChat API
- Генерацию текста
- Доступ к модели GigaChat

## Проверка в Docker

Если используете Docker, убедитесь, что переменные окружения передаются в контейнер:

```yaml
# docker-compose.yml
environment:
  GIGACHAT_CLIENT_ID: ${GIGACHAT_CLIENT_ID}
  GIGACHAT_CLIENT_SECRET: ${GIGACHAT_CLIENT_SECRET}
  GIGACHAT_SCOPE: ${GIGACHAT_SCOPE:-GIGACHAT_API_PERS}  # Опционально
```

## Логи для диагностики

После обновления кода, при ошибке 403 вы увидите детальные логи:

```
ERROR - GigaChat initialization failed with 403. Possible issues:
ERROR - Invalid credentials format
ERROR - Wrong scope (current: GIGACHAT_API_PERS, try: GIGACHAT_API_PERS or GIGACHAT_API_CORP)
ERROR - Credentials don't have required permissions
ERROR - Token expired (if using access token)
ERROR - Check credentials at https://developers.sber.ru/portal/products/gigachat
```

## Быстрая проверка

1. Проверьте логи agents service:
```bash
docker-compose logs agents-service | grep -i "403\|forbidden\|authentication"
```

2. Проверьте переменные окружения в контейнере:
```bash
docker-compose exec agents-service env | grep GIGACHAT
```

3. Перезапустите сервис после обновления credentials:
```bash
docker-compose restart agents-service
```

