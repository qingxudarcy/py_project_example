from inject import autoparams
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .config.service_config import Config, MysqlConfig


class MysqlClient:
    def __init__(self, config: Config):
        self.engine = self._create_async_engine(config.MYSQL_CONFIG, echo=config.is_dev)

    def _create_async_engine(
        self, config: MysqlConfig, echo: bool = False
    ) -> AsyncEngine:
        return create_async_engine(
            f"mysql+aiomysql://{config.USER}@{config.HOST}:{config.PORT}/example?user={config.USER}&password={config.PASSWORD}&charset=utf8mb4",
            echo=echo,
            pool_size=config.POOL_SIZE,
            max_overflow=config.MAX_OVERFLOW,
        )

    def get_async_session(self) -> AsyncSession:
        return AsyncSession(
            self.engine,
            expire_on_commit=False,
        )


@autoparams()
def bind_mysql_client(config: Config) -> MysqlClient:
    return MysqlClient(config)
