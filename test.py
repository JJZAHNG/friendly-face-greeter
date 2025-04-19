import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
for idx, v in enumerate(voices):
    # 不同平台 languages 类型可能是 bytes 或 str
    langs = []
    for lang in v.languages:
        if isinstance(lang, bytes):
            langs.append(lang.decode())
        else:
            langs.append(str(lang))
    print(f"[{idx}] Name: {v.name!r}, ID: {v.id!r}, Languages: {langs}")
