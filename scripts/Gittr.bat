@echo off
title Gittr
COLOR 07

cd /d "%~dp0.."
echo Current directory: %cd%
if exist ".git" (
    echo .git directory found.
) else (
    echo .git directory NOT found!
)

for /f "tokens=2 delims=:" %%O in ('icacls . ^| findstr /i "OWNER:"') do set "OWNER=%%O"
set "OWNER=%OWNER:~1%"  REM Trim leading space

echo Repo owner:%OWNER%
echo Current user:%USERNAME%

echo %OWNER% | findstr /I "%USERNAME%" >nul
if errorlevel 1 (
    echo [93mTaking ownership of the repo as you are not the owner...[0m
    takeown /f . /r /d y >nul
    icacls . /setaudit "%USERNAME%:F" /t >nul
    icacls . /grant:r "%USERNAME%:F" /t >nul
    icacls . /inheritance:e /t >nul
    echo [92mOwnership changed to %USERNAME%.[0m
)

git remote -v
if errorlevel 1 (
    echo [91mNo git remote found. Exiting.[97m
    timeout /t 5 >nul
    exit /b 1
)

if "%~1"=="" (
    set /p "Arg=[92mPlease provide a commit message:  [97m"
) else (
    set "Arg=%1"
)

cd /d "%~dp0.."
git remote -v >nul 2>&1
if errorlevel 1 (
    echo [91mNo git remote found. Exiting.[97m
    timeout /t 5 >nul
    exit /b 1
)

git add .
git commit -m "%Arg%"
git push
if errorlevel 1 (
    echo '[91mGit push failed. Please check your connection or repository settings.[0m'
    exit /b 1
) else (
    echo 'Gittr Pushed!'
)

Pause
Pause
