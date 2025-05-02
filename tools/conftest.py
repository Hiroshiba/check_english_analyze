import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension


@pytest.fixture
def snapshot_json(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """JSON形式のスナップショットテスト用fixture"""
    return snapshot.use_extension(JSONSnapshotExtension)
