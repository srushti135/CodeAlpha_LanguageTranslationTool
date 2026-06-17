**🌍 CodeAlpha Language Translation Tool – AI-Powered Multilingual Translation & Voice Assistant**
📌 Project Overview

The CodeAlpha Language Translation Tool is an advanced AI-powered multilingual translation and voice assistant developed using Python and Streamlit. The application enables users to translate text across multiple languages, automatically detect source languages, convert speech into text, generate speech from translated content, and maintain a searchable translation history.

This project extends the basic language translation functionality by integrating Natural Language Processing (NLP), Speech Recognition, Text-to-Speech Synthesis, Data Analytics, and Database Management into a single interactive platform.

Designed as part of the CodeAlpha Artificial Intelligence Internship Program, this application demonstrates the practical implementation of AI technologies in multilingual communication systems and real-world language assistance solutions.

## Features

- Modern Streamlit dashboard with sidebar navigation
- Source and target language selection
- Automatic language detection
- Text translation using Google Translate through `googletrans`
- Speech-to-text from microphone using `SpeechRecognition`
- Text-to-speech audio generation using `gTTS`
- Audio playback inside Streamlit
- Download translated text as TXT
- Download generated audio as MP3
- SQLite history storage
- Searchable translation history table
- Export translation history as CSV
- Translation statistics dashboard
- Character count and word count
- Copy-ready translated text area
- Empty input, unsupported language, microphone, and network error handling

## Tech Stack

- Python
- Streamlit
- Googletrans
- SpeechRecognition
- gTTS
- Pandas
- SQLite

## Project Structure

```text
Multilingual_AI_Translation_Assistant/
│
├── app.py
├── database.py
├── translator.py
├── requirements.txt
├── README.md
├── assets/
├── database/
│   └── translations.db
└── utils/
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/Multilingual_AI_Translation_Assistant.git
cd Multilingual_AI_Translation_Assistant
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

Windows:

```bash
venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

If `pyaudio` installation fails on Windows, install a compatible wheel or use:

```bash
pip install pipwin
pipwin install pyaudio
```

On Ubuntu/Debian:

```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

## Run the Application

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## How to Use

1. Open the Translator page.
2. Enter text manually or capture speech from the Voice Assistant page.
3. Choose source and target languages.
4. Enable automatic language detection if the source language is unknown.
5. Click Translate.
6. Generate speech audio for the translated output.
7. Download TXT or MP3 results.
8. View and export previous translations from the History page.

## Database

The app stores translation history in SQLite at:

```text
database/translations.db
```

Saved fields:

- Original Text
- Source Language
- Target Language
- Translated Text
- Timestamp

The database file is created automatically when the app starts.

## Screenshots
- Translator dashboard
- <img width="1361" height="677" alt="image" src="https://github.com/user-attachments/assets/50bd9758-371a-4d85-92d5-130494297694" />

- Voice assistant page
- <img width="1356" height="568" alt="image" src="https://github.com/user-attachments/assets/2c407574-d7fa-4171-9a46-9f7ae52e493a" />

- Statistics dashboard
- <img width="1360" height="575" alt="image" src="https://github.com/user-attachments/assets/6b7cd82a-47ce-48ab-9638-52ddcaf02b79" />

- Translation history table
- <img width="1099" height="565" alt="image" src="https://github.com/user-attachments/assets/4c9406ae-6963-47f3-9ff4-4bd355526d94" />


## Error Handling

The application handles:

- Empty text input
- Unsupported or missing language selections
- Google Translate/network failures
- Speech recognition timeout
- Unclear speech input
- Microphone permission or device errors
- Text-to-speech generation failures

## Production Notes

- `googletrans` uses unofficial Google Translate endpoints and can occasionally fail. For enterprise-grade deployment, replace it with Google Cloud Translation API, Azure Translator, or AWS Translate.
- Microphone capture works best on local machines. Browser-hosted or cloud deployments may need a browser-based audio recorder component.
- For public deployments, avoid committing `database/translations.db` if it contains personal user data.

## Future Enhancements

- User authentication
- Cloud database support with PostgreSQL
- Browser-native audio recording
- OCR image-to-translation workflow
- PDF and DOCX translation
- Batch translation from CSV files
- Favorite translations
- Admin analytics dashboard
- Docker deployment
- CI/CD with GitHub Actions

## Resume Project Description

Built a multilingual AI translation and voice assistant using Python, Streamlit, Google Translate, SpeechRecognition, gTTS, Pandas, and SQLite. The application supports automatic language detection, multilingual translation, microphone-based speech-to-text, text-to-speech audio playback, downloadable TXT/MP3 outputs, searchable translation history, CSV export, and analytics dashboard.

## License

This project is open for educational and portfolio use.
