from dotenv import load_dotenv;load_dotenv()
from pathlib import Path
from openai import OpenAI
client = OpenAI()

voice=['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']

for i in voice:
    Path("templates/chat_audio").mkdir(parents=True, exist_ok=True)
    speech_file_path = f"templates\\chat_audio\\{i}.mp3"
    response = client.audio.speech.create(
            model="tts-1",
            voice=i,
            input="안녕하세요 저는 OpenAI에서 제작한 tts입니다."
    )

    response.stream_to_file(speech_file_path)