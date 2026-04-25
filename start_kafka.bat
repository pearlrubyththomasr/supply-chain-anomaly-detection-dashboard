@echo off
REM Start Kafka with Docker Compose
echo.
echo 🚀 Starting Kafka...
docker-compose up -d
echo ✅ Kafka started!
echo.
echo 📝 Next steps:
echo 1. Open another terminal and run: python -m src.data_pipeline.producer
echo 2. Open another terminal and run: python -m src.dashboard.app
echo 3. Navigate to http://localhost:8050
echo.
pause
