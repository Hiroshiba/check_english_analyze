import pytest

from tools.process_syllable import UnifiedPhonemeInfo, process_syllables


@pytest.mark.parametrize(
    "text, expected_words, expected_phonemes, expected_stresses, expected_word_indexes, expected_phoneme_indexes, expected_syllable_indexes",
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
            [2, 2, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
            [0] * 17,
            list(range(17)),
            [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 7],
            id="basic",
        ),
        pytest.param(
            "hello, world!",
            ["hello", ",", "world", "!"],
            ["h", "ə", "l", "oʊ", ",", "w", "ɜː", "l", "d", "!"],
            [0, 0, 1, 1, 0, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 1, 2, 2, 2, 2, 3],
            list(range(10)),
            [0, 0, 1, 1, 2, 3, 3, 3, 3, 4],
            id="punct",
        ),
    ],
)
def test_syllable_param(
    text,
    expected_words,
    expected_phonemes,
    expected_stresses,
    expected_word_indexes,
    expected_phoneme_indexes,
    expected_syllable_indexes,
):
    """process_syllablesで音素・シラブル・ストレス・インデックス情報を取得し、期待値と比較"""
    result = process_syllables(text)
    assert isinstance(result, list)
    assert all(isinstance(x, UnifiedPhonemeInfo) for x in result)

    words_raw = [x.word for x in result]
    words = [w for i, w in enumerate(words_raw) if i == 0 or w != words_raw[i - 1]]
    assert words == expected_words

    phonemes = [x.phoneme for x in result]
    assert phonemes == expected_phonemes

    stresses = [x.stress for x in result]
    assert stresses == expected_stresses

    word_indexes = [x.word_index for x in result]
    assert word_indexes == expected_word_indexes

    phoneme_indexes = [x.phoneme_index for x in result]
    assert phoneme_indexes == expected_phoneme_indexes

    syllable_indexes = [x.syllable_index for x in result]
    assert syllable_indexes == expected_syllable_indexes
