# ---- Стадия 1: сборка зависимостей ----
# Полный python:3.12-alpine образ (не -slim), нужен для компиляции пакетов с C-расширениями
# (asyncpg, некоторые части pydantic-core) через gcc/musl-dev, которых нет в финальном образе.
FROM python:3.12-alpine AS builder

RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev

WORKDIR /app

COPY requirements.txt .
# Собираем колёса (wheels) отдельно — их потом скопируем в финальный образ БЕЗ компиляторов
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ---- Стадия 2: финальный образ ----
FROM python:3.12-alpine AS final

# Непривилегированный пользователь — требование безопасности из ТЗ
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Устанавливаем только собранные wheels — без компиляторов, отсюда и экономия размера
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels requirements.txt

# Только нужный код, не тесты/доки/локальные .env — держит образ маленьким
COPY src/ ./src/
COPY migration/ ./migration/
COPY alembic.ini .

# Владелец файлов — не root, и переключаемся на него ДО запуска процесса
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:8000/healthz', timeout=3).status == 200 else sys.exit(1)"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]