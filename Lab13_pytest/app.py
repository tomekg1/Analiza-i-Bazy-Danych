from textblob import TextBlob

def hello(name):
    output = f'Hello {name}'
    return output


def extract_sentiment(text):
    text = TextBlob(text)

    return text.sentiment.polarity

def text_contain_word(word: str, text: str):
    return word in text

def bubble_sort(lst: list):
    if not isinstance(lst, list):
        return None
    n = len(lst)
    for i in range(n):
        for j in range(n-i-1):
            if lst[j] > lst[j + 1]:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
    return lst