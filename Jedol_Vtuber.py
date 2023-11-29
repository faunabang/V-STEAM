import asyncio
import time
import keyboard
import threading
import pygame
from openai import OpenAI
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv;load_dotenv()  # openai_key .env 선언 사용
import re
import pyvts
from datetime import datetime
import os
import sys
import jedol1Fun as fun
import pytchat
import jedol2ChatDbFun as chatDB
import Jedol_Answer as ans
import utils.movement as move
from chat_GPT_tts import *
import utils.subtitle as sub
from elevenlabs import Voice, VoiceSettings, generate, play, set_api_key, stream


def setup():
    global feeling, total_characters, chat, chat_now, chat_prev, is_Speaking, owner_name, myvts, api_key, token, blacklist

    # to help the CLI write unicode characters to the terminal
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

    api_key = os.getenv('OPENAI_API_KEY')

    set_api_key("953f5c61f162a0b56da82fc2058d752e")

    total_characters = 0
    chat = ""
    chat_now = ""
    chat_prev = ""
    owner_name = "nabang"
    is_Speaking = False
    # token = fun.rnd_str(n=20, type="s")
    token = "sbSSVYcHdNlyXqLzbwRV"
    blacklist = ["Nightbot", "streamelements"]

    # Connect with Vtube studio api
    print("\n!!! ------------- Allow Vtube Studio API ------------- !!!\n")
    myvts = pyvts.vts()
    asyncio.run(move.connect_auth(myvts))
    feeling = ""

    with open ("texts/answer.txt", "w") as f:
        f.truncate(0)
    with open ("texts/chat.txt", "w") as f:
        f.truncate(0)


# function to get the user's input text
def type_text():
    # result = owner_name + " said " + input("Type your question: ")
    result = input("Type your question: ")
    
    with open("texts/chat.txt", "w", encoding="utf-8") as outfile:
        try:
            words = result.split()
            lines = [words[i:i+6] for i in range(0, len(words), 6)]
            for line in lines:
                outfile.write(" ".join(line) + "\n")
        except:
            print("Error writing to chat.txt")


def yt_livechat(video_id):
        global chat

        live = pytchat.create(video_id=video_id)
        print("--------------- Live Chat Start ---------------")
        while live.is_alive():
        # while True:
            try:
                for c in live.get().sync_items():
                    # Ignore chat from the streamer and Nightbot, change this if you want to include the streamer's chat
                    if c.author.name in blacklist:
                        continue
                    # if not c.message.startswith("!") and c.message.startswith('#'):
                    elif not c.message.startswith("!"):
                        # Remove emojis from the chat
                        chat_raw = re.sub(r':[^\s]+:', '', c.message)
                        chat_raw = chat_raw.replace('#', '')
                        # chat_author makes the chat look like this: "Nightbot: Hello". So the assistant can respond to the user's name
                        chat = c.author.name + ' : ' + chat_raw
                        print(chat)

                        with open("texts/chat.txt", 'w', encoding="utf-8") as f:
                            f.write(chat)
                        
                    time.sleep(1)
            except Exception as e:
                print("Error receiving chat: {0}".format(e))


def get_chat():
    print("--------------- V-Jedol Start ---------------")
    # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = str( datetime.now().date().today())
    print( f"vectorDB-faiss-jshs-{today}")

    vectorDB_folder = f"vectorDB-faiss-jshs-{today}"
    ans.vectorDB_create(vectorDB_folder)

    chatDB.setup_db()

    chat_prev = ""
    file_path = "texts/chat.txt"
    print("\n--------------------- setup finished ---------------------\n")
    print("getting chat.....\n")

    while True:
        try:
            if not os.path.exists(file_path):
                print("##############    no file    ################")
                time.sleep(1)
                continue

            with open(file_path, 'r', encoding="utf-8") as f:
                chat_now = f.read()

            # if chat_now.strip() == "":
            #     time.sleep(1)  # 파일이 비어있으면 잠시 대기
            #     continue

            if chat_now != chat_prev:    

                print(f"chat_prev: {chat_prev}, chat_now: {chat_now}")

                answer = ans.ai_response(
                    vectorDB_folder=vectorDB_folder,
                    query=chat_now,
                    token=token,
                )

                print(f"answer: {answer}")


                feeling = ''.join(re.findall(r'\((.*?)\)', answer))
                answer = re.sub(r'\(.*?\)', '', answer)

                print(f"feeling: {feeling}, answer: {answer}")

                chat_prev = chat_now
                # new_chat=[{"date": current_time },{"role": "user", "content": chat_now },{"role": "assistant", "content":answer}]
                # 이걸 chatDb에 저장하는 코드 추가

                while is_Speaking==True:
                    time.sleep(1)

                sub.generate_subtitle(chat_now,answer) # answer과 chat_now를 각각 texts/answer.txt, texts/selected_chat.txt에 저장

                chatGPT_tts(answer, feeling)

        except Exception as e:
            chat_now = f"Error reading file: {e}" 

def mp3_play(mp3_file, remove=True):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): 
            pygame.time.Clock().tick(10)
    
    finally:  
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        if remove:
            os.remove(mp3_file)

def chatGPT_tts(answer, feeling):
    global is_Speaking

    is_Speaking = True

    # client = OpenAI()

    # Path("templates/chat_audio").mkdir(parents=True, exist_ok=True)
    # response = client.audio.speech.create(
    #         model="tts-1",
    #         voice="fable",
    #         input=answer)
    # response.stream_to_file("templates/chat_audio/answer.mp3")

    # set_api_key("e5fb5e7333aea826329755e9f1459ab6")

    print("making audio.....")
    audio = generate(
        text=answer,
        voice=Voice(
            voice_id="XrExE9yKIg1WjnnlVkGX",
            settings=VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=False)
        ),
        model='eleven_multilingual_v2',
        stream = True
    )

    if not feeling == "":
        asyncio.run(move.trigger(myvts, feeling))
        print(f"Feeling {feeling} was made")
    else: print("No Feeling was made")

    print("Speaking Start")
    stream(audio)
    print("Speaking Finished")
    # mp3_play("templates/chat_audio/answer.mp3", True)

    if not feeling == "":
        asyncio.run(move.trigger(myvts, "clear"))
        print("Feeling Removed")
    
    # # Clear the text files after the assistant has finished speaking
    time.sleep(1)

    # with open ("texts/answer.txt", "w") as f:
    #     f.truncate(0)
    # with open ("texts/chat.txt", "w") as f:
    #     f.truncate(0)
    
    is_Speaking = False
    print("\ngetting new chat.....\n")


if __name__ == "__main__":
    try:
        video_id = input("video id : ")
        setup()

        # Threading is used to capture livechat and answer the chat at the same time
        t = threading.Thread(target=get_chat)
        t.start()

        yt_livechat(video_id)


        # print("Press and Hold Right Shift to record audio or Press Left Shift to type text")
        # while True:
        #     if keyboard.is_pressed('LEFT_SHIFT'):
        #         type_text()
            
    except KeyboardInterrupt:
        t.join()
        print("\n--------------------- Stopped ---------------------\n")
