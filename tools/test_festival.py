from tools.festival import PhonemeInfo, festival


def test_festival_basic():
    """festivalを用いて音素・シラブル・ストレス情報を取得できる"""
    text = "internationalization"
    result = festival(text, verbose=False)
    assert isinstance(result, list)
    assert all(isinstance(x, PhonemeInfo) for x in result)

    words = {x.word for x in result}
    assert "internationalization" in words

    # ストレス情報が1または0で含まれること
    stresses = {x.stress for x in result if x.stress is not None}
    assert 1 in stresses or 0 in stresses
