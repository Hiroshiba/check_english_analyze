import tempfile
from pathlib import Path

from syrupy.assertion import SnapshotAssertion

from tools.process_alignment import alignment


# TODO: multi_speaker=Trueのテストを追加する
def test_alignment_with_real_data(snapshot: SnapshotAssertion):
    """tools/data/*.txt, *.wavを使ってalignment関数の出力をスナップショットテスト"""
    text_glob = "tools/data/*.txt"
    wav_glob = "tools/data/*.wav"
    with tempfile.TemporaryDirectory() as temp_dir:
        result = alignment(
            text_glob, wav_glob, multi_speaker=False, output_textgrid_dir=Path(temp_dir)
        )
        assert result == snapshot
