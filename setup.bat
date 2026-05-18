@echo off
echo ============================================
echo    RoadRescue - One Click Setup
echo ============================================
echo.

echo [1/5] Installing required packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: pip install failed. Trying with py...
    py -m pip install -r requirements.txt
)
echo Done.
echo.

echo [2/5] Creating database migrations...
python manage.py makemigrations accounts
python manage.py makemigrations services
python manage.py makemigrations emergency
python manage.py makemigrations core
echo Done.
echo.

echo [3/5] Applying migrations...
python manage.py migrate
echo Done.
echo.

echo [4/5] Seeding sample data...
python manage.py seed_data
echo Done.
echo.

echo [5/5] Starting server...
echo.
echo ============================================
echo   Server running at http://127.0.0.1:8000/
echo.
echo   Portal:    http://127.0.0.1:8000/
echo   Register:  http://127.0.0.1:8000/register/
echo   Login:     http://127.0.0.1:8000/login/
echo   Dashboard: http://127.0.0.1:8000/dashboard/
echo   Admin:     http://127.0.0.1:8000/admin/
echo   API Docs:  http://127.0.0.1:8000/api/docs/
echo.
echo   Admin login: admin@roadrescue.com / admin123
echo ============================================
echo.
python manage.py runserver
