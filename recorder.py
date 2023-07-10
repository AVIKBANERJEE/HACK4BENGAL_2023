from multiprocessing.connection import Client

import speech_recognition as sr

from controller import parse

recognizer = sr.Recognizer()
address = ("localhost", 6000)
conn = Client(address=address, authkey=b"HACK4BENGAL")

with sr.Microphone() as source:
    audio = recognizer.adjust_for_ambient_noise(source)
    recognizer.energy_threshold = 2000
    recognizer.dynamic_energy_threshold = False
    print(f"Threshold value after calibration: {recognizer.energy_threshold}")
    while True:
        try:
            print("Please speak:")
            audio = recognizer.listen(source)
            print("Recognizing...")
            conn.send(audio.get_wav_data())
            resp = conn.recv()
            command = resp["text"].strip().lower()
            print(f"Command: {command}")
            try:
                parse(command)
            except Exception as e:
                print("Something went wrong.")

            if "stop connection" in resp["text"].strip():
                print("Goodbye!")
                conn.send("close")
                conn.close()
                break

        except KeyboardInterrupt:
            conn.close()
            break

        except Exception as e:
            print(e)
            print("Sorry, could not understand.")
