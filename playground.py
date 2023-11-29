from elevenlabs import Voice, VoiceSettings, voices, generate, play, set_api_key, clone, stream

set_api_key("e5fb5e7333aea826329755e9f1459ab6")

# def text_stream():
#     yield "Hi there, I'm Eleven "
#     # yield "I'm a text to speech API "

# audio_stream = generate(
#     text=text_stream(),
#     voice="Matilda",
#     model="eleven_multilingual_v2",
#     stream=True
# )

# stream(audio_stream)

# voices = voices()
# audio = generate(text="Hello there!", voice=voices[0])
# print(voices)

audio = generate(
    text="안녕? 나는 제돌이라고 해.",
    voice=Voice(
        voice_id='XrExE9yKIg1WjnnlVkGX',
        # settings=None
        settings=VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=False)
    ),
    model="eleven_multilingual_v2"
)   

play(audio)

# with open('output.mp3', 'wb') as f:
#     for i,chunk in enumerate(audio):
#         if chunk: f.write(chunk) 