import chardet

with open("ProverbsADay\\proverbs.txt", "rb") as f:
    raw_data = f.read()
    result = chardet.detect(raw_data)
    detected_encoding = result['encoding']
print(detected_encoding)
#file = open("ProverbsADay\\proverbs.txt", encoding=detected_encoding)
