import sys
from datetime import datetime
from pathlib import Path
import traceback
from app.utils import *
from flask import Flask, request, Response
import threading
import queue
import time

api = Flask(__name__)
fifo_queue = queue.Queue()

try:
    from vits.synthesizer import Synthesizer

    synthesizer = Synthesizer(TTS_CONFIG_PATH)

    if TTS_MODEL_PATH.exists():
        synthesizer.load_model(TTS_MODEL_PATH)
    else:
        download_model("G_600000.pth")
        synthesizer.load_model(TTS_MODEL_PATH)

    synthesizer.init_speaker_map(SPEAKER_CONFIG)

except ImportError as err:
    print(err)


def synthesize(params):
    audio_data = synthesizer.synthesize(params["text"], params["speaker_id"], params)
    cur_timestamp = datetime.now().strftime("%m%d%f")

    save_file_name = "_".join([cur_timestamp])
    save_file_path = Path(params["out_path"])
    save_audio(
        save_file_path, save_file_name, audio_data, params["file_export_ext"]
    )

    return save_file_name


def play_audio_queue():
    while (True):
        while fifo_queue.empty():
            time.sleep(1)

        item = fifo_queue.get()
        play_audio(item)
        fifo_queue.task_done()


def play_audio(file_path):
    if PLATFORM == "Windows":
        winsound.PlaySound(str(file_path), winsound.SND_ASYNC)
    elif PLATFORM == "Linux" or PLATFORM == "Darwin":
        if file_path[-3:] == "ogg":
            audio = AudioSegment.from_ogg(str(file_path))
        if file_path[-3:] == "wav":
            audio = AudioSegment.from_wav(str(file_path))
        play(audio)


def exit_clean_up():
    tmp_files = Path("static_web", "tmp").glob("*.*")
    for f in tmp_files:
        f.unlink()
    sys.exit(0)


@api.route('/tts', methods=['POST'])
def post_tts():
    ttsdata = request.json
    params = {}

    params["speaker_id"] = ttsdata["speaker_id"]
    params["speech_speed"] = float(ttsdata["speech_speed"])
    params["speech_var_a"] = float(ttsdata["speech_var_a"])
    params["speech_var_b"] = float(ttsdata["speech_var_b"])
    params["file_export_ext"] = "ogg"
    params["text"] = ttsdata["text"]
    params["out_path"] = "export/audio"

    try:
        filename = synthesize(params)
    except Exception as err:
        print(err)
        traceback.print_tb(err.__traceback__)
    
    if(ttsdata["playback"]):
        fifo_queue.put(params["out_path"] + "/" + filename + "." + params["file_export_ext"])

    return Response('{"filename": "' + filename + '.ogg"}', status=200, mimetype='application/json')

if __name__ == "__main__":
    threading.Thread(target=play_audio_queue).start()
    api.run() 
    exit_clean_up()