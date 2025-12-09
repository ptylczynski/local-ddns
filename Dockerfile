# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --user --no-cache-dir -r requirements.txt
# Expose the port the app runs on
EXPOSE 8000
# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
