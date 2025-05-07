import tempfile
from pathlib import Path

from syrupy.assertion import SnapshotAssertion

from tools.extract_feature import AlignedPhonemeInfo, extract_aligned_feature


def test_extract_aligned_feature_with_real_data(snapshot_json: SnapshotAssertion):
    """tools/data/*.txt, *.wavを使ってextract_aligned_feature関数の出力をスナップショットテスト"""
    text_glob = "tools/data/*.txt"
    wav_glob = "tools/data/*.wav"
    with tempfile.TemporaryDirectory() as temp_dir:
        result = extract_aligned_feature(
            text_glob, wav_glob, Path(temp_dir), verbose=False, output_textgrid=False
        )
        assert result == snapshot_json
