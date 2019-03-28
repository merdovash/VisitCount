rmdir /Q /S build
rmdir /Q /S dist
git pull origin room_update
pyinstaller bisitor.spec