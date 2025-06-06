@echo off
title Gittr
COLOR 07

:: Admin Check ::
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [91m[ERROR] Not running as administrator. Relaunching with admin rights...
    timeout /t 3 >nul
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Ensure .git ::
cd /d "%~dp0.."
if exist ".git" (
    echo [92m[INFO] Repo found! && echo 
    echo [93m[WARNING] Forcing Ownership... && echo 
    call :OWN
) else (
    echo  [91m[ERROR] .git directory NOT found! && echo
)

:OWN
echo  [0mCurrent user:  [96m%USERNAME% && echo 
takeown /f . /r /d y >nul
icacls . /grant:r "%USERNAME%:F" /t >nul
icacls . /inheritance:e /t >nul
echo [92m[INFO] Ownership changed to  [96m%USERNAME%. && echo [0m

git remote -v && echo 
if errorlevel 1 (
    echo [91m[ERROR] No git remote found. Exiting in 5s && echo 
    timeout /t 5 >nul
    exit /b 1
)

if "%~1"=="" (
    set /p "Arg=[92mPlease provide a commit message: [95m" && echo [0m
) else (
    set "Arg=%1"
)

cd /d "%~dp0.."
git remote -v >nul 2>&1 && echo 
if errorlevel 1 (
    echo [91m[ERROR] No git remote found. Exiting.[96m && echo 
    timeout /t 5 >nul
    exit /b 1
)

git add .
git commit -m "%Arg%"
git push
if errorlevel 1 (
    echo [91m[ERROR] Git push failed. Please check your connection or repository settings.[0m && echo 
    exit /b 1
) else (
    echo [42m[.35]Gittr Pushed!
)

Pause
Pause
