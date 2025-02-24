# face_blur_app
Python app w/ GUI to select faces to blur from a directory of images/videos. Can determine blur strength

# Create a virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Install required packages
pip install ultralytics opencv-python ffmpeg-python

REM Run the Python script
python face_blur_app.py

REM Pause to see the output
pause
