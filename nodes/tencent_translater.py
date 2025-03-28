import json
import requests

class TencentTranslater:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        input_types = {
            "required": {
                "Text_A": ("STRING", {"multiline": True}),
                "Text_B": ("STRING", {"multiline": True}),
                "Translate": ("BOOLEAN", {"default": True}),
                "From": ([
                    "Auto",         
                    "English",      # 英语
                    "中文",         # 中文 (zh)
                    "Deutsch",      # 德语
                    "Español",      # 西班牙语
                    "Français",     # 法语
                    "Italiano",     # 意大利语
                    "日本語",        # 日语
                    "한국어",        # 韩语
                    "Português",    # 葡萄牙语
                    "Русский",      # 俄语
                    "العربية",      # 阿拉伯语
                    "ไทย",          # 泰语
                    "Türkçe",       # 土耳其语
                    "Tiếng Việt"    # 越南语
                ], {"default": "Auto"}),
                "To": ([
                    "English",      # 英语
                    "中文",         # 中文 (zh)
                    "Deutsch",      # 德语
                    "Español",      # 西班牙语
                    "Français",     # 法语
                    "Italiano",     # 意大利语
                    "日本語",        # 日语
                    "한국어",        # 韩语
                    "Português",    # 葡萄牙语
                    "Русский",      # 俄语
                    "العربية",      # 阿拉伯语
                    "ไทย",          # 泰语
                    "Türkçe",       # 土耳其语
                    "Tiếng Việt"    # 越南语
                ], {"default": "English"}),
            }
        }
        return input_types

    CATEGORY = "KayTool/Translate"

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("A", "B")
    FUNCTION = "translate_texts"

    DESCRIPTION = "The TencentTranslater node provides a convenient way to translate text using the Tencent Translate API. It supports multiple languages and allows users to specify source and target languages."

    def initData(self, source_lang, target_lang, translate_text):
        return {
            "header": {
                "fn": "auto_translation",
                "client_key": "browser-chrome-110.0.0-Mac OS-df4bd4c5-a65d-44b2-a40f-42f34f3535f2-1677486696487"
            },
            "type": "plain",
            "model_category": "normal",
            "source": {
                "lang": source_lang,
                "text_list": [translate_text]
            },
            "target": {
                "lang": target_lang
            }
        }

    def translate_texts(self, Text_A, Text_B, Translate, From, To):
        if not Translate:
            
            return (Text_A, Text_B)

        
        lang_map = {
            "Auto": None,         
            "English": "en",
            "中文": "zh",
            "Deutsch": "de",
            "Español": "es",
            "Français": "fr",
            "Italiano": "it",
            "日本語": "ja",
            "한국어": "ko",
            "Português": "pt",
            "Русский": "ru",
            "العربية": "ar",
            "ไทย": "th",
            "Türkçe": "tr",
            "Tiếng Việt": "vi"
        }

        source_lang = lang_map[From]
        target_lang = lang_map[To]

        def translate_text(text):
            if not text:
                return ""
            url = 'https://transmart.qq.com/api/imt'
            post_data = self.initData(source_lang, target_lang, text)
            headers = {
                'Content-Type': 'application/json',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                'referer': 'https://transmart.qq.com/zh-CN/index'
            }
            try:
                response = requests.post(url, headers=headers, data=json.dumps(post_data))
                result = response.json()
                if response.status_code != 200 or 'auto_translation' not in result or not result['auto_translation']:
                    error_msg = f"Translation failed with status code {response.status_code}: {result.get('error_msg', 'Unknown error')}"
                    print(error_msg)
                    raise RuntimeError(error_msg)
                return '\n'.join(result['auto_translation'])
            except Exception as e:
                error_msg = f"Error during translation: {str(e)}"
                print(error_msg)
                raise RuntimeError(error_msg)

        translated_a = translate_text(Text_A)
        translated_b = translate_text(Text_B)

        return (translated_a, translated_b)