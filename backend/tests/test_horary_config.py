import os
import sys
import logging


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from horary_config import HoraryConfig


def test_horary_config_loads_without_unexpected_logs(caplog):
    HoraryConfig.reset()
    with caplog.at_level(logging.INFO, logger="horary_config"):
        cfg = HoraryConfig()
        assert cfg.config is not None
    assert len(caplog.records) == 1
    assert caplog.records[0].message.startswith("Loaded horary configuration")

