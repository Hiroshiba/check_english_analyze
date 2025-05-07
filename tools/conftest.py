import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension

from utility.logger_utility import logging_setting


def pytest_configure(config: pytest.Config):
    """pytestのverbosityに応じてloggingのレベルを変更する"""
    logging_setting(verbose=config.get_verbosity() > 0)


@pytest.fixture
def snapshot_json(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """JSON形式のスナップショットテスト用fixture"""
    return snapshot.use_extension(JSONSnapshotExtension)
