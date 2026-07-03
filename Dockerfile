FROM python:3.11-slim

WORKDIR /app

RUN addgroup --system finspark && adduser --system --ingroup finspark finspark

COPY pyproject.toml uv.lock* ./
RUN pip install uv && uv sync --frozen --no-dev

COPY src/ ./src/

RUN chown -R finspark:finspark /app
USER finspark

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
