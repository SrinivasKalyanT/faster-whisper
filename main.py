# pip install fastapi uvicorn websockets faster-whisper soundfile numpy

from fastapi import FastAPI, WebSocket, UploadFile, File, Form
from faster_whisper import WhisperModel
import numpy as np
import soundfile as sf
import io
import uuid
from fastapi.responses import HTMLResponse


app = FastAPI()
# model = WhisperModel("small", device="cpu", compute_type="int8")

model = WhisperModel("/Users/srinivaskalyan/Downloads/faster-whisper-small", device="cpu", compute_type="int8")


"""
# Live transcription via WebSocket with language is only english
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        # Assume data is a raw WAV or PCM chunk; adapt as needed
        audio, sr = sf.read(io.BytesIO(data), dtype="float32")
        if sr != 16000:
            # Resample if needed
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        # segments, _ = model.transcribe(audio, beam_size=5, task="transcribe")
        # text = " ".join([segment.text for segment in segments])
        # await websocket.send_text(text)

        segments, _ = model.transcribe(audio, beam_size=5, task="transcribe", word_timestamps=True)
        text = " ".join([word.word for segment in segments for word in (segment.words or [])])
        await websocket.send_text(text)
"""

# Live transcription via WebSocket with language support(By default it is English)
# Add this to your websocket endpoint in main.py
from fastapi import Query

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, language: str = Query("en")):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        try:
            audio, sr = sf.read(io.BytesIO(data), dtype="float32")
        except RuntimeError:
            import librosa
            audio, sr = librosa.load(io.BytesIO(data), sr=16000, mono=True)
        if sr != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        segments, _ = model.transcribe(audio, beam_size=5, task="translate", language=language, word_timestamps=True)
        text = " ".join([word.word for segment in segments for word in (segment.words or [])])
        await websocket.send_text(text)

# Transcribe audio from a file upload
# Faster Whisper API
@app.post("/transcribe/")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("en")  # Default language is English
):
    conversation_id = str(uuid.uuid4())  # Generate a unique conversation ID
    audio_bytes = await file.read()
    audio, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32")
    if sr != 16000:
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    segments, info = model.transcribe(
        audio,
        beam_size=5,
        task="transcribe",
        language=language
    )
    result = {
        "conversation_id": conversation_id,
        "detected_language": info.language,
        "language_probability": info.language_probability,
        "segments": [
            {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            }
            for segment in segments
        ]
    }
    return result



# # pip install fastapi uvicorn websockets faster-whisper soundfile numpy librosa

# from fastapi import FastAPI, WebSocket, UploadFile, File, Form
# from faster_whisper import WhisperModel
# import numpy as np
# import soundfile as sf
# import io
# import uuid

# app = FastAPI()
# model = WhisperModel("small", device="cpu", compute_type="int8")

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_bytes()
#         # Assume data is a raw WAV or PCM chunk; adapt as needed
#         try:
#             audio, sr = sf.read(io.BytesIO(data), dtype="float32")
#         except RuntimeError:
#             # Fallback for unsupported formats (e.g., MP3)
#             import librosa
#             audio, sr = librosa.load(io.BytesIO(data), sr=16000, mono=True)
#         if sr != 16000:
#             import librosa
#             audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
#         segments, _ = model.transcribe(audio, beam_size=5, task="transcribe", word_timestamps=True)
#         text = " ".join([word.word for segment in segments for word in (segment.words or [])])
#         await websocket.send_text(text)

# @app.post("/transcribe/")
# async def transcribe_audio(
#     file: UploadFile = File(...),
#     language: str = Form("en")  # Default language is English
# ):
#     conversation_id = str(uuid.uuid4())  # Generate a unique conversation ID
#     audio_bytes = await file.read()
#     try:
#         audio, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32")
#     except RuntimeError:
#         # Fallback for unsupported formats (e.g., MP3)
#         import librosa
#         audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
#     if sr != 16000:
#         import librosa
#         audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
#     segments, info = model.transcribe(
#         audio,
#         beam_size=5,
#         task="transcribe",
#         language=language
#     )
#     result = {
#         "conversation_id": conversation_id,
#         "detected_language": info.language,
#         "language_probability": info.language_probability,
#         "segments": [
#             {
#                 "start": segment.start,
#                 "end": segment.end,
#                 "text": segment.text
#             }
#             for segment in segments
#         ]
#     }
#     return