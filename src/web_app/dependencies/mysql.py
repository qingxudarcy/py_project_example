from inject import autoparams
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)

from .config.service_config import Config, MysqlConfig


class MysqlClient:
    def __init__(self, config: Config):
        self.engine = self._create_engine(
            config.MYSQL_CONFIG, echo=config.IS_DEVELOPMENT
        )

    def _create_engine(self, config: MysqlConfig, echo: bool = False) -> AsyncEngine:
        return create_async_engine(
            f"mysql+aiomysql://{config.USER}@{config.HOST}:{config.PORT}/example?user={config.USER}&password={config.PASSWORD}&charset=utf8mb4",
            echo=echo,
        )

    @property
    def get_session(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(self.engine, expire_on_commit=False)


@autoparams()
def bind_mysql_client(config: Config) -> MysqlClient:
    return MysqlClient(config)
