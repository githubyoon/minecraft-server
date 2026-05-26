@echo off
git pull
java -jar paper-1.21.11-132.jar nogui
git add .
git commit -m "Auto Save"
git push
pause
