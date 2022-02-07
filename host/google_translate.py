import googletrans
import requests
import json
from typing import Union

translator = googletrans.Translator()


def translate(text: str, source: str, target: str, api_key: Union[str, None]) -> str:
    if api_key:
        response = requests.post(
            f'https://translation.googleapis.com/language/translate/v2?key={api_key}',
            headers={
                'Content-Type': 'application/json; charset=utf-8'
            },
            data=json.dumps({
                'q': text,
                'source': source,
                'target': target,
                'format': 'text'
            }),
        )

        if response.status_code != 200:
            raise Exception(f'status code: {response.status_code}')

        translated_text = json.loads(response.text)['data']['translations'][0]['translatedText']
    else:
        translated_text = translator.translate(text, src=source, dest=target).text

    return translated_text
