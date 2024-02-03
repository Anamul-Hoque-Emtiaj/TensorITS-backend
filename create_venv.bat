@echo off

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
pip install -r requirements.txt

REM Install torch
pip install torch torchvision torchaudio

REM Install Other module
pip install django djangorestframework corsheaders drf_spectacular firebase-admin

echo Virtual environment created, activated, and requirements installed.
