@echo off
REM Start the data producer
echo.
echo 📤 Starting Data Producer...
python -m src.data_pipeline.producer
pause
