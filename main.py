import speech_recognition as sr
import requests
import keyboard
import io
import tempfile
import openai
import wave
import os,sys
import subprocess
import time
import random
with open("gpt_key.txt",'r') as f:
    key = f.read()
openai.api_key = key

# Initialize the recognizer
r = sr.Recognizer()

# Start listening to the microphone
def listen_for_speech():
    print("Hold down the 'v' key to speak.")

    # Create an empty buffer to store audio data
    buffer = io.BytesIO()

    # Set a flag to indicate if speech recognition is in progress
    is_listening = False

    while True:
        if keyboard.is_pressed("v"):
            if not is_listening:
                print("Listening...")

                # Start recording audio
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)  # Optional: Adjust for ambient noise

                    # Continuously listen until 'v' key is released
                    while keyboard.is_pressed("v"):
                        audio = r.listen(source)
                        buffer.write(audio.get_wav_data())

                is_listening = True
        else:
            if is_listening:
                print("Recognizing...")

                # Save the audio data to a temporary WAV file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir='.') as temp_audio:
                    with wave.open(temp_audio.name, "wb") as wav_file:
                        wav_file.setnchannels(1)  # Mono channel
                        wav_file.setsampwidth(2)  # 2 bytes per sample
                        wav_file.setframerate(44100)  # 44.1 kHz sample rate
                        wav_file.writeframes(buffer.getvalue())

                # Close the temporary WAV file

                # Use the speech recognition API
                try:
                    file = open(temp_audio.name, "rb")
                    transcription = openai.Audio.transcribe("whisper-1", file)
                    # Print the recognized text
                    file.close()

                    while True:
                        answer = input(f"Did you say '{transcription.text}'? (Y/N): ")
                        if answer == 'Y':
                            # Delete the temporary WAV file
                            os.remove(temp_audio.name)

                            # Clear the buffer and reset the flag
                            buffer.seek(0)
                            buffer.truncate()
                            is_listening = False
                            return transcription.text
                        elif answer == 'N':
                            print("Please make sure you wait for 5 seconds after holding the 'v' key before speaking.")
                            os.remove(temp_audio.name)
                            return listen_for_speech()
                        else:
                            print("Invalid input. Please enter 'Y' or 'N'.")

                except requests.exceptions.RequestException as e:
                    print("There is an error. Let's try again.")

def textToCommand(speech):
    prompt = "You are a personal assistant for my computer so whenever i ask you for a task i want you to respond with cmd prompt in order to do that task . When i give you a task respond only with the prompt without any extra explanation or extra text that explains what to do.\n"
    command = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt+speech}
        ],
        temperature=0
    )
    subprocess.run(command.choices[0].message.content, shell=True, capture_output=True, text=True)
# Start listening for speech

def logo():
    clear = "\x1b[0m"
    colors = [32]

    x = """


     _______  _______ _________   _______  _______  _______ _________ _______ _________ _______  _       _________
    (  ____ \(  ____ )\__   __/  (  ___  )(  ____ \(  ____ \\__   __/(  ____ \\__   __/(  ___  )( (    /|\__   __/
    | (    \/| (    )|   ) (     | (   ) || (    \/| (    \/   ) (   | (    \/   ) (   | (   ) ||  \  ( |   ) (   
    | |      | (____)|   | |     | (___) || (_____ | (_____    | |   | (_____    | |   | (___) ||   \ | |   | |   
    | | ____ |  _____)   | |     |  ___  |(_____  )(_____  )   | |   (_____  )   | |   |  ___  || (\ \) |   | |   
    | | \_  )| (         | |     | (   ) |      ) |      ) |   | |         ) |   | |   | (   ) || | \   |   | |   
    | (___) || )         | |     | )   ( |/\____) |/\____) |___) (___/\____) |   | |   | )   ( || )  \  |   | |   
    (_______)|/          )_(     |/     \|\_______)\_______)\_______/\_______)   )_(   |/     \||/    )_)   )_(   



    \033[0;37;41m[ Coded by TN Legend ]
    """
    for N, line in enumerate(x.split("\n")):
        sys.stdout.write("\x1b[1;%dm%s%s\n" % (random.choice(colors), line, clear))
        time.sleep(0.05)

logo()
text=listen_for_speech()
textToCommand(text)
