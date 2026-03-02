@echo off
title ROOP Auto-Installer
color 0A

echo.
echo ========================================
echo   ROOP AUTO-INSTALLER
echo ========================================
echo.
echo This will automatically install all
echo required packages for ROOP Face Swapper
echo.
pause

python auto_install.py

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo You can now run the application with:
echo   - LAUNCHER.bat
echo   - run.bat
echo   - python app.py
echo.
pause
