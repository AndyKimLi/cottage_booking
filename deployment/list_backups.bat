@echo off
REM Скрипт для просмотра доступных бэкапов (Windows)
REM Использование: list_backups.bat

set BACKUP_DIR=.\backups

echo 📁 Доступные резервные копии:
echo ================================

if not exist "%BACKUP_DIR%" (
    echo ❌ Папка бэкапов не найдена: %BACKUP_DIR%
    exit /b 1
)

REM Подсчитываем общее количество бэкапов
for /f %%i in ('dir "%BACKUP_DIR%\*.sql*" 2^>nul ^| find /c ".sql"') do set TOTAL_BACKUPS=%%i

if %TOTAL_BACKUPS%==0 (
    echo ❌ Бэкапы не найдены
    exit /b 1
)

echo 📊 Всего бэкапов: %TOTAL_BACKUPS%
echo.

REM Показываем бэкапы с информацией о размере и дате
for %%f in ("%BACKUP_DIR%\*.sql*") do (
    for %%a in ("%%f") do (
        set FILENAME=%%~nxa
        set SIZE=%%~za
        set DATE=%%~ta
        
        REM Определяем тип файла
        echo %%f | findstr /C:".gz" >nul
        if %errorlevel%==0 (
            set TYPE=📦 Сжатый
        ) else (
            set TYPE=📄 Обычный
        )
        
        echo !TYPE! ^| !SIZE! bytes ^| !DATE! ^| !FILENAME!
    )
)

echo.
echo 💡 Для восстановления используйте:
echo    restore_db.bat backup_YYYYMMDD_HHMMSS.sql.gz

