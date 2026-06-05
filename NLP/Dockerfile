FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and assets
COPY main.py .
COPY prompts/ ./prompts/
COPY input/ ./input/
COPY output/ ./output/

# Expose port
EXPOSE 8000

# Run the FastAPI service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
