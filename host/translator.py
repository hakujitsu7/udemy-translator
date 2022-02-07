import requests
import re
from google_translate import translate
from typing import Dict, List, Union


class Translator:
    def __init__(self):
        self.source: str = ''
        self.target: str = ''
        self.api_key: Union[str, None] = None

        self.scripts: List[str] = []
        self.sentences: List[str] = []

        self.script_table: List[List] = []
        self.sentence_table: List[Dict] = []

        self.translation_cache: List[Dict] = []
        self.translated_scripts: List[str] = []

    def initialize(self, webvtt_url: str, source: str, target: str, api_key: Union[str, None]) -> None:
        # 번역 옵션을 저장합니다.
        self.source = source
        self.target = target
        self.api_key = api_key

        # URL로부터 WebVTT를 읽어들입니다.
        response = requests.get(webvtt_url)

        if response.status_code != 200:
            raise Exception(f'status code: {response.status_code}')

        vtt = response.text

        # WebVTT로부터 자막을 추출합니다.
        self.scripts = []

        for script in vtt.split('\n\n'):
            if script == 'WEBVTT':
                continue

            self.scripts.append(script[script.index('\n') + 1:].strip().replace('\n', ' '))

        # 마침표를 판별하는 정규표현식입니다.
        period_regex = re.compile(r'(\.[^ \w]*) ')

        # 마침표를 기준으로 문장을 나눕니다.
        self.sentences = period_regex.sub('\\1\n', ' '.join(self.scripts)).split('\n')

        # 자막을 글과 마침표로 나눕니다.
        parsed_scripts = []

        for script in self.scripts:
            parsed_scripts.append(period_regex.sub('\n.\n', f'{script} ').strip().split('\n'))

        # 각 자막에 포함된 문장의 인덱스들을 저장합니다.
        # 예를 들어, 5번 자막에 2번 문장과 3번 문장이 포함되어 있다면
        # script_table[5] 의 값은 [2, 3]이 됩니다.
        self.script_table = [[] for i in range(len(self.scripts))]

        current_sentence_index = 0
        for i in range(len(parsed_scripts)):
            for part in parsed_scripts[i]:
                if part == '.':
                    current_sentence_index += 1
                    continue

                self.script_table[i].append(current_sentence_index)

        # 각 문장의 자막별 어절 포함 비율, 번역 여부를 저장합니다.
        # 예를 들어, 총 20개의 어절로 이루어진 3번 문장이 5번 자막에 5개의 어절만큼, 6번 자막에 15개의 어절만큼 포함되어 있다면
        # sentence_table[3]['scripts']의 값은 {5: 0.25, 6: 0.75}가 됩니다.
        self.sentence_table = [
            {
                'scripts': {},
                'is_translated': False
            } for i in range(len(self.sentences))
        ]

        current_sentence_index = 0
        for i in range(len(parsed_scripts)):
            for part in parsed_scripts[i]:
                if part == '.':
                    # 어절의 개수를 비율로 변환합니다.
                    total_words = sum(self.sentence_table[current_sentence_index]['scripts'].values())
                    for key in self.sentence_table[current_sentence_index]['scripts'].keys():
                        self.sentence_table[current_sentence_index]['scripts'][key] /= total_words

                    current_sentence_index += 1
                    continue

                # 각 자막에 포함된 어절의 개수를 셉니다.
                if i not in self.sentence_table:
                    self.sentence_table[current_sentence_index]['scripts'][i] = 0
                self.sentence_table[current_sentence_index]['scripts'][i] += part.count(' ') + 1

        # 번역 중인 자막들을 저장하는 번역 캐시입니다.
        self.translation_cache = [{} for i in range(len(self.scripts))]

        # 최종적으로 번역 완료된 자막들을 저장합니다.
        self.translated_scripts = ['' for i in range(len(self.scripts))]

    def get_script_index(self, script: str) -> int:
        return self.scripts.index(script)

    def get_script_count(self):
        return len(self.scripts)

    def translate_script(self, script_index: int) -> None:
        # 이미 번역된 자막이라면 건너뜁니다.
        if self.translated_scripts[script_index]:
            return

        # 자막에 포함된 문장들을 번역합니다.
        for sentence_index in self.script_table[script_index]:
            # 이미 번역된 문장이라면 건너뜁니다.
            if self.sentence_table[sentence_index]['is_translated']:
                continue

            # 아직 번역되지 않은 문장을 번역합니다.
            translated_sentence = translate(self.sentences[sentence_index], self.source, self.target, self.api_key)
            self.sentence_table[sentence_index]['is_translated'] = True

            # 번역된 문장들을 어절 단위로 나눕니다.
            words = translated_sentence.split(' ')
            total_words = len(words)

            # 원어 자막에서의 자막별 어절 포함 비율을 토대로, 번역된 문장의 어절을 각 자막에 분배합니다.
            last_key = list(self.sentence_table[sentence_index]['scripts'].keys())[-1]
            for key in self.sentence_table[sentence_index]['scripts'].keys():
                if key != last_key:
                    split_count = int(round(total_words * self.sentence_table[sentence_index]['scripts'][key]))

                    self.translation_cache[key][sentence_index] = ' '.join(words[:split_count])
                    words = words[split_count:]
                else:
                    self.translation_cache[key][sentence_index] = ' '.join(words)

        # 자막에 포함된 문장들을 문장 번호 기준으로 정렬한 뒤, 이어 붙입니다.
        translated_script = ' '.join(dict(sorted(self.translation_cache[script_index].items())).values())
        self.translated_scripts[script_index] = translated_script

    def get_translated_script(self, script_index: int) -> str:
        return self.translated_scripts[script_index]
