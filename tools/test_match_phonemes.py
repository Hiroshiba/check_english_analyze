import pytest

from tools.match_phonemes import match_phonemes


@pytest.mark.parametrize(
    "festival_phonemes, phonemizer_phonemes, expected_mapping",
    [
        pytest.param(
            ["b", "aa", "t"],
            ["b", "ɑː", "t"],
            [(0, 0), (1, 1), (2, 2)],
            id="simple_1_to_1",
        ),
        pytest.param(
            ["b", "er", "t"],
            ["b", "ʌ", "ɹ", "t"],
            [(0, 0), (1, 1), (1, 2), (2, 3)],
            id="one_to_many",
        ),
        pytest.param(
            ["b", "aa", "r", "t"],
            ["b", "ɑːɹ", "t"],
            [(0, 0), (1, 1), (2, 1), (3, 2)],
            id="many_to_one",
        ),
        pytest.param(
            ["b", "aa", "r", "er", "t"],
            ["b", "ɑːɹ", "ʌ", "ɹ", "t"],
            [(0, 0), (1, 1), (2, 1), (3, 2), (3, 3), (4, 4)],
            id="mixed_mapping",
        ),
    ],
)
def test_match_phonemes_valid_cases(
    festival_phonemes, phonemizer_phonemes, expected_mapping
):
    """match_phonemesで音素列のアライメントを取得し、期待値と比較"""
    result = match_phonemes(festival_phonemes, phonemizer_phonemes)
    assert isinstance(result, list)
    assert all(isinstance(x, tuple) and len(x) == 2 for x in result)
    assert result == expected_mapping


def test_match_phonemes_invalid_mapping():
    """存在しないマッピングの場合はValueErrorが発生することを確認"""
    with pytest.raises(ValueError, match="アライメント失敗"):
        match_phonemes(["xyz"], ["abc"])


def test_match_phonemes_empty_input():
    """空の入力の場合は空のリストを返すことを確認"""
    result = match_phonemes([], [])
    assert result == []
