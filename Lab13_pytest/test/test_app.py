from app import hello
from app import extract_sentiment
from app import text_contain_word
from app import bubble_sort
import pytest


def test_hello():
    got = hello("Aleksandra")
    want = "Hello Aleksandra"

    assert got == want

testdata1 = ["I think today will be a great day"]

@pytest.mark.parametrize('sample', testdata1)
def test_extract_sentiment(sample):

    sentiment = extract_sentiment(sample)

    assert sentiment > 0

testdata2 = [
    ('There is a duck in this text', 'duck', True),
    ('There is nothing here', 'duck', False)
    ]

@pytest.mark.parametrize('sample, word, expected_output', testdata2)
def test_text_contain_word(sample, word, expected_output):

    assert text_contain_word(word, sample) == expected_output


bubble_sort_testdata = [
    ([1, 6, 6, 9, 4, 15, -3], [-3, 1, 4, 6, 6, 9, 15]),
    ([3, 0.065, 69, 199, -0.077, 0, -46], [-46, -0.077, 0, 0.065, 3, 69, 199])
]

@pytest.mark.parametrize('input_list, sorted_list', bubble_sort_testdata)
def test_bubble_sort(input_list, sorted_list):
    assert bubble_sort(input_list) == sorted_list