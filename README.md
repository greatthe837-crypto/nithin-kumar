# Wildlife Acoustics — Sound Classification Website

A responsive educational/research showcase with a real audio-analysis endpoint powered by Google's pretrained YAMNet model via TensorFlow Hub.

## Features
- Premium forest-green and gold responsive website
- Project overview, wildlife education and workflow sections
- Audio upload interface
- Server-side AI sound-event predictions (top 5 AudioSet labels)
- WAV, FLAC, OGG and AIFF input; maximum 25 MB / 120 seconds

## Requirements
- Python 3.10 or 3.11 recommended
- Internet connection on first run (YAMNet model and AudioSet labels download on first analysis)
- Several GB of free disk space and RAM recommended for TensorFlow

## Run locally (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## Run locally (macOS / Linux)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000.

## About the AI
YAMNet is a pretrained general sound-event classifier trained on AudioSet. It returns ranked sound categories, some of which are wildlife-related (for example bird, frog or insect categories). It does **not** guarantee identification of a particular species and should not be used as a conservation decision tool without validation. For reliable species-level monitoring, the next development step is to fine-tune or integrate a model trained on curated regional wildlife recordings.

## Next steps
1. Add your college/team details and project documentation.
2. Add a dataset of verified local wildlife calls.
3. Fine-tune a species-specific model and evaluate precision/recall.
4. Add secure hosting, upload limits, privacy policy and production error handling before public deployment.

## Notes
- The page uses externally hosted Unsplash photos and Google Fonts; replace them with licensed/local assets if publishing.
- MP3 is not accepted in this starter version. Convert MP3 to WAV before uploading.
- The Flask development server is for local testing only. Use a production WSGI server and HTTPS for deployment.
