"""Translation, language detection, speech recognition, and audio helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path

import speech_recognition as sr
from googletrans import LANGCODES, LANGUAGES, Translator
from gtts import gTTS


class TranslationError(RuntimeError):
    """Raised when a translation provider operation fails."""


LANGUAGE_OPTIONS = {
    language.title(): code for code, language in sorted(LANGUAGES.items(), key=lambda item: item[1])
}


def get_language_code(language_name: str) -> str:
    if not language_name:
        raise TranslationError("Please select a language.")

    normalized = language_name.strip().lower()
    if normalized in LANGUAGES:
        return normalized
    if normalized in LANGCODES:
        return LANGCODES[normalized]

    raise TranslationError(f"Unsupported language: {language_name}")


def get_language_name(language_code: str) -> str:
    return LANGUAGES.get(language_code, language_code).title()


class TranslationService:
    def __init__(self) -> None:
        self._translator = Translator()

    def detect_language(self, text: str) -> tuple[str, float]:
        self._validate_text(text)
        try:
            detection = self._translator.detect(text)
            return detection.lang, float(detection.confidence or 0)
        except Exception as exc:
            raise TranslationError(
                "Language detection failed. Please check your internet connection."
            ) from exc

    def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str | None = None,
    ) -> dict[str, str]:
        self._validate_text(text)
        destination_code = get_language_code(target_language)

        try:
            if source_language:
                source_code = get_language_code(source_language)
            else:
                detected_code, _ = self.detect_language(text)
                source_code = detected_code

            translated = self._translator.translate(
                text,
                src=source_code,
                dest=destination_code,
            )
        except TranslationError:
            raise
        except Exception as exc:
            raise TranslationError(
                "Translation failed. The translation service may be unavailable."
            ) from exc

        return {
            "original_text": text,
            "translated_text": translated.text,
            "source_code": source_code,
            "source_language": get_language_name(source_code),
            "target_code": destination_code,
            "target_language": get_language_name(destination_code),
        }

    @staticmethod
    def _validate_text(text: str) -> None:
        if not text or not text.strip():
            raise TranslationError("Please enter text before translating.")


def synthesize_speech(text: str, language_code: str) -> bytes:
    if not text or not text.strip():
        raise TranslationError("No translated text is available for speech output.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_path = Path(temp_audio.name)

        tts = gTTS(text=text, lang=language_code)
        tts.save(str(temp_path))
        audio_bytes = temp_path.read_bytes()
        temp_path.unlink(missing_ok=True)
        return audio_bytes
    except Exception as exc:
        raise TranslationError(
            "Text-to-speech generation failed for the selected language."
        ) from exc


def recognize_speech_from_microphone(language_code: str) -> str:
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=20)
        return recognizer.recognize_google(audio, language=language_code)
    except sr.WaitTimeoutError as exc:
        raise TranslationError("Listening timed out. Please try again.") from exc
    except sr.UnknownValueError as exc:
        raise TranslationError("Could not understand the recorded audio.") from exc
    except sr.RequestError as exc:
        raise TranslationError(
            "Speech recognition service is unavailable. Please check your connection."
        ) from exc
    except OSError as exc:
        raise TranslationError(
            "Microphone access failed. Check your device permissions and PyAudio setup."
        ) from exc
