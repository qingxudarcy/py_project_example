import os
from typing import Dict, Tuple, Any, Union

from inject import autoparams
from pydantic import ValidationError, Field, BaseModel
from pydantic.dataclasses import dataclass
from dynaconf import Dynaconf
from loguru import logger


class WebServiceConfig(BaseModel):
    HOST: str
    PORT: int


class MysqlConfig(BaseModel):
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str


class LogConfig(BaseModel):
    LOG_LEVEL: str
    USE_JSON: bool


@dataclass
class Config:
    LOG_CONFIG: LogConfig = Field(default_factory=lambda: LogConfig())
    WEB_SERVICE_CONFIG: WebServiceConfig = Field(
        default_factory=lambda: WebServiceConfig()
    )
    MYSQL_CONFIG: MysqlConfig = Field(default_factory=lambda: MysqlConfig())

    PROJECT_PATH: str = Field(
        default=os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    )
    IS_DEVELOPMENT: bool = os.getenv("ENV", "development") == "development"


@autoparams()
def bind_config() -> Config:
    config_path = os.path.join(Config.PROJECT_PATH, "configs")
    config_file_path = os.path.join(
        config_path, os.getenv("config_file", "setting.yaml")
    )
    settings = Dynaconf(
        settings_files=[config_file_path],
        load_dotenv=True,
        environments=True,
        envvar_prefix=False,
    )

    config_dict: Dict[str, Tuple[str, Union[str, Any]]] = {
        config_name: value
        for config_name, value in settings.as_dict().items()
        if config_name in Config.__pydantic_fields__
    }

    try:
        _config: Config = Config(**config_dict)
    except ValidationError as e:
        logger(f"[read config] error: {e.errors()}")

    logger.info("-------------init config-------------")
    logger.info(f"config dict: {config_dict}")

    return _config
