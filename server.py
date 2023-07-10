from multiprocessing.connection import Listener

from whisper_jax import FlaxWhisperPipline

pipeline = FlaxWhisperPipline("openai/whisper-medium.en")

address = ("localhost", 6000)
continue_listening = True

while continue_listening:
    listener = Listener(address, authkey=b"HACK4BENGAL")
    print("Listening...")
    conn = listener.accept()

    while True:
        try:
            mesg = conn.recv()
            if mesg == "close":
                conn.close()
                continue_listening = False
                break
            speech_to_txt = pipeline(mesg)
            conn.send(speech_to_txt)
        except EOFError:
            break

    listener.close()
