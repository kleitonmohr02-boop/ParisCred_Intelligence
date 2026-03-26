@echo off
cd C:\ParisCred_Intelligence
echo === Attempting Git Push ===
echo.
echo Checking remote...
git remote -v
echo.
echo Checking branch...
git branch -avv
echo.
echo Starting push to GitHub...
git push -u origin main
echo.
echo Push complete!
pause
