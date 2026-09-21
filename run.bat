@echo off
echo ========================================================
echo Sanskrit Shloka Analysis RAG System - Sushruta Samhita
echo ========================================================
echo.

if "%1"=="" goto menu
if "%1"=="ingest" goto ingest
if "%1"=="retrieval" goto retrieval
if "%1"=="pipeline" goto pipeline
if "%1"=="webapp" goto webapp
if "%1"=="streamlit" goto streamlit
if "%1"=="test" goto test

:menu
echo Choose an option:
echo 1. Ingest Data (Create Vector Store)
echo 2. Test Retrieval (CLI Semantic Search)
echo 3. Run 7-Step Pipeline (CLI Shloka Analysis)
echo 4. Launch FastAPI Web App (Primary HTML/CSS/JS UI)
echo 5. Run Automated Tests
echo 6. Launch Legacy Streamlit UI
echo 7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto ingest
if "%choice%"=="2" goto retrieval
if "%choice%"=="3" goto pipeline
if "%choice%"=="4" goto webapp
if "%choice%"=="5" goto test
if "%choice%"=="6" goto streamlit
if "%choice%"=="7" goto exit
goto menu

:ingest
echo.
echo Running Ingestion...
python scripts/ingest.py
pause
goto menu

:retrieval
echo.
set /p q="Enter search query (press Enter for default): "
if "%q%"=="" (
    python scripts/test_retrieval.py
) else (
    python scripts/test_retrieval.py -q "%q%"
)
pause
goto menu

:pipeline
echo.
set /p s="Enter shloka number (1, 3, 5, 9, 11, 12, 13, 14, 16): "
if "%s%"=="" set s=1
python scripts/run_pipeline.py --shloka %s%
pause
goto menu

:webapp
echo.
echo Launching FastAPI Web App at http://127.0.0.1:8000...
python -m uvicorn src.server:app --host 127.0.0.1 --port 8000 --reload
pause
goto menu

:streamlit
echo.
echo Launching Legacy Streamlit Web App...
streamlit run app/streamlit_app.py
pause
goto menu

:test
echo.
echo Running Pytest Suite...
python -m pytest tests/ -v
pause
goto menu

:exit
echo Exiting...
