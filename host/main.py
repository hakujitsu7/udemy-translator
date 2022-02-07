import nativemessaging
import json
from translator import Translator

translator = Translator()

while True:
    message = json.loads(nativemessaging.get_message())

    if message['message'] == 'INITIALIZE':
        translator.initialize(message['webvtt_url'], message['source'], message['target'], message['api_key'])

    elif message['message'] == 'TRANSLATE_SCRIPT':
        script_index = translator.get_script_index(message['script'])

        translator.translate_script(script_index)
        translated_script = translator.get_translated_script(script_index)

        nativemessaging.send_message(nativemessaging.encode_message({
            'message': 'SCRIPT_TRANSLATED',
            'translated_script': translated_script
        }))

        pre_translate_count = 2
        script_count = translator.get_script_count()

        for i in range(1, pre_translate_count + 1):
            if script_index + i >= script_count:
                break

            translator.translate_script(script_index + i)
