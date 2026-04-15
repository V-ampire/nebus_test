import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ConnectionPool:
    def __init__(self, size):
        self.size = size
        self.connections = [f"conn_{i}" for i in range(size)]
        self.index = 0

    def acquire(self):
        conn = self.connections[self.index]
        self.index = (self.index + 1) % self.size
        return conn

    async def close(self):
        self.connections = []


@dataclass
class HttpSession:
    """Emulate HTTP requests."""

    pool: ConnectionPool

    async def post(self, url: str, payload: dict):
        data = json.dumps(payload)
        conn = self.pool.acquire()
        logger.info(f"[POST] url={url}")
        logger.info(f"[POST] json={data}")
        logger.info(f"[POOL] using {conn}")
