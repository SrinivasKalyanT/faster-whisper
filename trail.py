# from faster_whisper import WhisperModel

# model_size = "small"

# # Run on GPU with FP16
# # model = WhisperModel(model_size, device="cuda", compute_type="float16")

# # or run on GPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")
# # or run on CPU with INT8
# # model = WhisperModel(model_size, device="cpu", compute_type="int8")

# segments, info = model.transcribe("/Users/srinivaskalyan/Documents/faster-whisper/faster-whisper/OUTPUTS/Arabic_Conversation_resampled.wav", beam_size=5)

# print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

# for segment in segments:
#     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))



from faster_whisper import WhisperModel

model_size = "small"

model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, info = model.transcribe(
    "/Users/srinivaskalyan/Documents/faster-whisper/faster-whisper/OUTPUTS/Arabic_Conversation_resampled.wav",
    beam_size=5,
    task="translate"  # Add this line to translate to English
)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))