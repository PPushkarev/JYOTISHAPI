# 1. Base image: using lightweight Python 3.11
FROM python:3.11-slim

# 2. Install system dependencies for Swiss Ephemeris (C-code compilation)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy and install requirements first (to optimize Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the project source code maintaining your specific structure
# - app/ folder (FastAPI)
# - core_files/ folder (Support modules)
# - core.py (Main engine)
COPY app/ ./app/
COPY core_files/ ./core_files/
COPY core.py .

# 6. Ensure logs directory exists
RUN mkdir -p logs

# 7. Set Environment Variables
# Force logs to be unbuffered (immediate output)
ENV PYTHONUNBUFFERED=1
# Critical: Make sure Python can find core.py and core_files
ENV PYTHONPATH=/app

# 8. Expose the API port (Railway сам переназначит его, но для ясности оставим)
EXPOSE 8080

# 9. Запуск через uvicorn (обязательно указываем хост 0.0.0.0)
# Используем конструкцию, которая берет PORT из настроек Railway
CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port ${PORT:-8080}"]