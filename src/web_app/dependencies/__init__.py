import inject
from inject import Binder

from dependencies.config.service_config import Config, bind_config
from dependencies.mysql import MysqlClient, bind_mysql_client
from dependencies.logger import set_up_logger


def instance_bind(bind: Binder) -> None:
    bind.bind_to_constructor(Config, bind_config)
    bind.bind_to_constructor(MysqlClient, bind_mysql_client)


inject.configure(instance_bind, bind_in_runtime=False)

set_up_logger(inject.instance(Config))
