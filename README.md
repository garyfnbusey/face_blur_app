# face_blur_app
Python app w/ GUI to select faces to blur from a directory of images/videos. Can determine blur strength. The blurred faces will not overlap the excluded subject (in my testing)

## INSTALLATION

1. Clone repo
1. Create a virtual environment

```

python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

1. Install required packages

```
pip install ultralytics opencv-python ffmpeg-python
```

1. Run the Python script
   
```
python face_blur_app.py

```

## USAGE

1. Select a directory containing images or videos.
2. Images will appear 1 at a time. The green box indicates the face to leave alone, red boxes will be blurred. Press ENTER
3. When finished a new subdir will appear called `output` containing a copy of your files with the targeted faces blurred.

### Adjusting blur

Run the Script: The GUI now shows a slider labeled "Blur Strength" set to 5.
Adjust the Slider: Move it to set the blur intensity (1 = light, 20 = heavy).
Select Folder: Click "Select Folder," choose your images/videos, and proceed as before.
Test: The blur strength applies to all processed files in that run.

**Testing:**
Light Blur: Set to 1 or 2—faces should be slightly softened but recognizable.
Heavy Blur: Set to 15 or 20—faces should be completely obscured.
Current Setting: At 5, it should match what you’ve seen so far.

**Customization**
Range: If 1-20 isn’t enough, adjust `from_` and `to_` in the slider (e.g., 0.5 to 30).

TODO:
Kernel Size Option: If you’d rather control kernel size, I could add another slider for that. Will see if it's needed
