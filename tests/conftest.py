import pytest
import logging
import os
from io import StringIO

import sea
from sea.test.fixtures import *  # noqa


@pytest.fixture
def logstream():
    return StringIO()


@pytest.fixture
def app(logstream):
    os.environ.setdefault('SEA_ENV', 'testing')
    logger = logging.getLogger('sea')
    h = logging.StreamHandler(logstream)
    # NOTE:
    # Python 3.14 在解释器关闭阶段会调用 logging.shutdown()，
    # 默认的 StreamHandler.close() 会把底层的 StringIO 也关掉。
    # 而我们的多进程 server 在退出时的信号处理里仍然会调用 logger.warning，
    # 这在 3.14 上就会触发 “ValueError: I/O operation on closed file” 的
    # Logging error（见 CI 日志）。
    #
    # 为了避免这种测试阶段的噪声和退出码问题，我们让 handler.close 成为 no-op，
    # 这样 logging.shutdown() 不会关闭 StringIO，后续日志写入仍然是安全的。
    h.close = lambda: None
    logger.addHandler(h)
    root = os.path.join(os.path.dirname(__file__), 'wd')
    app = sea.create_app(root)
    yield app
    logger.removeHandler(h)
    sea._app = None
