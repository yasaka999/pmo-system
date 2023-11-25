from openai import OpenAI
client = OpenAI()
openai_api_key = "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"
endpoint = "https://api.openai.com/v1/audio/transcriptions"

audio_file= open("../files/test.mp3", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)

print(transcript)