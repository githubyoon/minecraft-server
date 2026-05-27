@echo off
rem git pull
java -Xms16G -Xmx16G -jar paper-1.21.11-132.jar nogui
git add .
git commit -m "Auto Save"
git push
pause
