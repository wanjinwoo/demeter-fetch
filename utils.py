from datetime import datetime

from _typing import *


def convert_to_config(conf_file: dict) -> Config:
    to_type = ToType[conf_file["to"]["type"]]
    save_path = "./"
    if "save_path" in conf_file["to"]:
        save_path = conf_file["to"]["save_path"]
    minute_config = MinuteConfig()
    if "minute" in conf_file["to"]:
        enable_proxy = conf_file["to"]["minute"]["enable_proxy"]
        minute_config.enable_proxy = enable_proxy

    to_config = ToConfig(to_type, save_path, minute_config)

    chain = ChainType[conf_file["from"]["chain"]]
    data_source = DataSource[conf_file["from"]["datasource"]]
    pool_address = conf_file["from"]["pool_address"]

    from_config = FromConfig(chain, data_source, pool_address)
    match data_source:
        case DataSource.file:
            if "file" not in conf_file["from"]:
                raise RuntimeError("should have [from.file]")
            file_path = None
            if "file_path" in conf_file["from"]["file"]:
                file_path = conf_file["from"]["file"]["file_path"]
            folder = None
            if "folder" in conf_file["from"]["file"]:
                folder = conf_file["from"]["file"]["folder"]
            proxy_file_path = None
            if "proxy_file_path" in conf_file["from"]["file"]:
                proxy_file_path = conf_file["from"]["file"]["proxy_file_path"]
            if file_path is None and folder is None:
                raise RuntimeError("file_path and folder can not both null")
            if to_config.minute_config.enable_proxy and not proxy_file_path:
                raise RuntimeError("no proxy file")

            from_config.file = FileConfig(file_path, folder, proxy_file_path)
        case DataSource.rpc:
            if "rpc" not in conf_file["from"]:
                raise RuntimeError("should have [from.rpc]")
            proxy_file_path = None
            if "proxy_file_path" in conf_file["from"]["rpc"]:
                proxy_file_path = conf_file["from"]["rpc"]["proxy_file_path"]
            auth_string = None
            if "auth_string" in conf_file["from"]["rpc"]:
                auth_string = conf_file["from"]["rpc"]["auth_string"]
            http_proxy = None
            if "http_proxy" in conf_file["from"]["rpc"]:
                http_proxy = conf_file["from"]["rpc"]["http_proxy"]
            end_point = conf_file["from"]["rpc"]["end_point"]
            start_height = int(conf_file["from"]["rpc"]["start_height"])
            end_height = int(conf_file["from"]["rpc"]["end_height"])
            batch_size = int(conf_file["from"]["rpc"]["batch_size"])
            if to_config.minute_config.enable_proxy and not proxy_file_path:
                raise RuntimeError("no proxy file")
            from_config.rpc = RpcConfig(end_point=end_point,
                                        start_height=start_height,
                                        end_height=end_height,
                                        batch_size=batch_size,
                                        auth_string=auth_string,
                                        http_proxy=http_proxy,
                                        proxy_file_path=proxy_file_path)
        case DataSource.big_query:
            if "big_query" not in conf_file["from"]:
                raise RuntimeError("should have [from.big_query]")
            start_time = datetime.strptime(conf_file["from"]["big_query"]["start"], "%Y-%m-%d").date()
            end_time = datetime.strptime(conf_file["from"]["big_query"]["end"], "%Y-%m-%d").date()
            auth_file = conf_file["from"]["big_query"]["auth_file"]
            from_config.big_query = BigQueryConfig(start_time, end_time, auth_file)

    return Config(from_config, to_config)