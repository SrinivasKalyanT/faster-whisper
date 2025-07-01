"""
# This is a client script that captures audio from the microphone and sends it to a WebSocket server for transcription.
# It uses the `sounddevice` library to capture audio and the `websockets` library to communicate with the server.
# The audio is sent in chunks of 10 seconds, and the transcription result is printed to the console.

# import asyncio
# import websockets
# import sounddevice as sd
# import numpy as np
# import soundfile as sf
# import io

# SAMPLE_RATE = 16000
# CHUNK_DURATION = 10  # seconds

# async def send_audio():
#     uri = "ws://localhost:8000/ws"
#     async with websockets.connect(uri) as websocket:
#         print("Connected to server. Start speaking...")
#         while True:
#             audio = sd.rec(int(CHUNK_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
#             sd.wait()
#             buf = io.BytesIO()
#             sf.write(buf, audio, SAMPLE_RATE, format='WAV')
#             await websocket.send(buf.getvalue())
#             text = await websocket.recv()
#             print("Transcription:", text)

# if __name__ == "__main__":
#     asyncio.run(send_audio())
"""


# # It is working fine But with no overlapping audio chunks.
# # 
# import asyncio
# import websockets
# import sounddevice as sd
# import numpy as np
# import soundfile as sf
# import io
# from queue import Queue

# SAMPLE_RATE = 16000
# CHUNK_DURATION = 2  # seconds

# audio_queue = Queue()

# def audio_callback(indata, frames, time, status):
#     audio_queue.put(indata.copy())

# async def send_audio():
#     uri = "ws://localhost:8000/ws"
#     async with websockets.connect(uri) as websocket:
#         print("Connected to server. Start speaking...")
#         with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
#                             blocksize=int(SAMPLE_RATE * CHUNK_DURATION), callback=audio_callback):
#             while True:
#                 audio = audio_queue.get()
#                 buf = io.BytesIO()
#                 sf.write(buf, audio, SAMPLE_RATE, format='WAV')
#                 await websocket.send(buf.getvalue())
#                 text = await websocket.recv()
#                 print("Transcription:", text)

# if __name__ == "__main__":
#     asyncio.run(send_audio())

"""
# Implementation with overlapping audio chunks(By default trancription is in English):

# Overlapping audio chunks can be achieved by adjusting the `blocksize` parameter in the `InputStream` to a smaller value, allowing for more frequent audio captures. This way, the audio stream can capture shorter segments of audio, which can then be sent to the server for transcription.
# This example captures audio in chunks of 2 seconds with a 0.5-second overlap, allowing for smoother transitions between audio segments.

import asyncio
import websockets
import sounddevice as sd
import numpy as np
import soundfile as sf
import io
from queue import Queue

SAMPLE_RATE = 16000
CHUNK_DURATION = 2      # seconds per chunk
OVERLAP_DURATION = 0.5  # seconds of overlap

audio_queue = Queue()
overlap_samples = int(OVERLAP_DURATION * SAMPLE_RATE)
prev_audio = np.zeros((0, 1), dtype='float32')

def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

async def send_audio():
    global prev_audio
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        print("Connected to server. Start speaking...")
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
                            blocksize=int(SAMPLE_RATE * CHUNK_DURATION), callback=audio_callback):
            while True:
                audio = audio_queue.get()
                # Concatenate overlap from previous chunk
                if prev_audio.shape[0] > 0:
                    audio_to_send = np.concatenate([prev_audio, audio], axis=0)
                else:
                    audio_to_send = audio
                # Update prev_audio for next chunk
                if audio.shape[0] >= overlap_samples:
                    prev_audio = audio[-overlap_samples:]
                else:
                    prev_audio = audio
                # Write to buffer and send
                buf = io.BytesIO()
                sf.write(buf, audio_to_send, SAMPLE_RATE, format='WAV')
                await websocket.send(buf.getvalue())
                text = await websocket.recv()
                print("Transcription:", text)

if __name__ == "__main__":
    asyncio.run(send_audio())

"""


# Implementation with overlapping audio chunks(By default trancription is in English):
# This example captures audio in chunks of 2 seconds with a 0.5-second overlap, allowing for smoother transitions between audio segments.
# The language can be specified as a command line argument, defaulting to English if not provided.
# 
# To run the client, use the command:
# python client.py [language]
# where [language] is the desired language code (e.g., "en" for English, "fr" for French, etc.).
import asyncio
import websockets
import sounddevice as sd
import numpy as np
import soundfile as sf
import io
from queue import Queue
import sys

SAMPLE_RATE = 16000
CHUNK_DURATION = 2      # seconds per chunk
OVERLAP_DURATION = 0.5  # seconds of overlap

# Get language from command line or default to "en"
if len(sys.argv) > 1:
    language = sys.argv[1]
else:
    language = "en"

audio_queue = Queue()
overlap_samples = int(OVERLAP_DURATION * SAMPLE_RATE)
prev_audio = np.zeros((0, 1), dtype='float32')

def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

# async def send_audio():
#     global prev_audio
#     uri = f"ws://localhost:8000/ws?language={language}"
#     async with websockets.connect(uri) as websocket:
#         print(f"Connected to server. Start speaking... (Language: {language})")
#         with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
#                             blocksize=int(SAMPLE_RATE * CHUNK_DURATION), callback=audio_callback):
#             while True:
#                 audio = audio_queue.get()
#                 # Concatenate overlap from previous chunk
#                 if prev_audio.shape[0] > 0:
#                     audio_to_send = np.concatenate([prev_audio, audio], axis=0)
#                 else:
#                     audio_to_send = audio
#                 # Update prev_audio for next chunk
#                 if audio.shape[0] >= overlap_samples:
#                     prev_audio = audio[-overlap_samples:]
#                 else:
#                     prev_audio = audio
#                 # Write to buffer and send
#                 buf = io.BytesIO()
#                 sf.write(buf, audio_to_send, SAMPLE_RATE, format='WAV')
#                 await websocket.send(buf.getvalue())
#                 text = await websocket.recv()
#                 print("Transcription:", text)

SILENCE_THRESHOLD = 0.01  # Adjust this value as needed


def is_silent(audio, threshold=SILENCE_THRESHOLD):
    return np.sqrt(np.mean(audio**2)) < threshold

async def send_audio():
    global prev_audio
    uri = f"ws://localhost:8000/ws?language={language}"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to server. Start speaking... (Language: {language})")
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
                            blocksize=int(SAMPLE_RATE * CHUNK_DURATION), callback=audio_callback):
            while True:
                audio = audio_queue.get()
                # Concatenate overlap from previous chunk
                if prev_audio.shape[0] > 0:
                    audio_to_send = np.concatenate([prev_audio, audio], axis=0)
                else:
                    audio_to_send = audio
                # Update prev_audio for next chunk
                if audio.shape[0] >= overlap_samples:
                    prev_audio = audio[-overlap_samples:]
                else:
                    prev_audio = audio
                # Only send if not silent
                if not is_silent(audio_to_send):
                    buf = io.BytesIO()
                    sf.write(buf, audio_to_send, SAMPLE_RATE, format='WAV')
                    await websocket.send(buf.getvalue())
                    text = await websocket.recv()
                    print("Transcription:", text)
                # else: skip sending silent chunk

if __name__ == "__main__":
    asyncio.run(send_audio())