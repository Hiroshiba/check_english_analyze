import pytest

from tools.process_phonemizer import PhonemeInfo, phonemizer_espeak


@pytest.mark.parametrize(
    "text, expected_words, expected_phonemes, expected_stresses",
    [
        pytest.param(
            "internationalization",
            ["internationalization"],
            [
                "ɪ",
                "n",
                "t",
                "ɚ",
                "n",
                "æ",
                "ʃ",
                "ə",
                "n",
                "ə",
                "l",
                "ᵻ",
                "z",
                "eɪ",
                "ʃ",
                "ə",
                "n",
            ],
            [2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            id="basic",
        ),
        pytest.param(
            "hello, world!",
            ["hello", ",", "world", "!"],
            [
                "h",
                "ə",
                "l",
                "oʊ",
                ",",
                "w",
                "ɜː",
                "l",
                "d",
                "!",
            ],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            id="punct",
        ),
    ],
)
def test_phonemizer_param(text, expected_words, expected_phonemes, expected_stresses):
    """phonemizer+espeakで音素・ストレス情報を取得し、期待値と比較"""
    result = phonemizer_espeak(text, verbose=False)
    assert isinstance(result, list)
    assert all(isinstance(x, PhonemeInfo) for x in result)

    words_raw = [x.word for x in result]
    words = [w for i, w in enumerate(words_raw) if i == 0 or w != words_raw[i - 1]]
    assert words == expected_words

    phonemes = [x.phoneme for x in result]
    assert phonemes == expected_phonemes

    stresses = [x.stress for x in result]
    assert stresses == expected_stresses
