 python3 -m venv venv  - створити віртуальне оточення
 source venv/bin/activate - запустити віртуальне оточення macos
 source venv/Scripts/activate - запустити віртуальне оточення windows
 python3 scriptName.py - запустити скрипт
 pip install -r requirements.txt - встановити залежності зі списку з requirements.txt
 pip freeze > requirements.txt  - створити список залежностей в файлі requirements.txt для того щоб правильно інсталювати проект ( юзай цю команду після того як додаєш нову бібліотеку в python)
 python -m PyInstaller --onefile --windowed --icon=app.ico --add-data "app.ico;." -p . -p firebaseMonitor --hidden-import config_manager --hidden-import firebase_manager --hidden-import log_window --hidden-import logger --hidden-import monitor --hidden-import settings_window main.py - build app
