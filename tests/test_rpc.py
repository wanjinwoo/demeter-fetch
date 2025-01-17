import os
import unittest
from datetime import datetime

import toml

import demeter_fetch._typing as typing
from demeter_fetch import constants, utils
from demeter_fetch.source_rpc.eth_rpc_client import EthRpcClient, HeightCacheManager, ContractConfig, query_event_by_height
from demeter_fetch.source_rpc.uniswap import query_uniswap_pool_logs, append_proxy_log


class UniLpDataTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.config = toml.load("./config.toml")

        super(UniLpDataTest, self).__init__(*args, **kwargs)

    # ==========lines=========================
    def test_query_blockno_from_time(self):
        value = utils.ApiUtil.query_blockno_from_time(typing.ChainType.ethereum, datetime(2023, 5, 8), True, "127.0.0.1:7890")
        self.assertTrue(value == 17212079, "height not right")

    def remove_tmp_file(self, paths: []):
        for p in paths:
            if os.path.exists(os.path.join(self.config["to_path"], p)):
                os.remove(os.path.join(self.config["to_path"], p))

    def test_query_event_by_height(self):
        self.remove_tmp_file(["polygon-0x45dda9cb7c25131df268515131f647d726f50608-42447801-42448800.tmp.pkl"])

        client = EthRpcClient(self.config["end_point"], "127.0.0.1:7890")
        height_cache = HeightCacheManager(typing.ChainType.polygon, self.config["to_path"])
        files = query_event_by_height(
            chain=typing.ChainType.polygon,
            client=client,
            contract_config=ContractConfig(
                "0x45dda9cb7c25131df268515131f647d726f50608",
                [constants.SWAP_KECCAK, constants.BURN_KECCAK, constants.COLLECT_KECCAK, constants.MINT_KECCAK],
            ),
            start_height=42447801,
            end_height=42448800,  # diff = 999, will save in one batch
            height_cache=height_cache,
            save_path=self.config["to_path"],
            save_every_query=2,
            batch_size=500,
            skip_timestamp=True,
        )
        print(files)
        self.assertTrue(len(files) == 1)

    def test_query_event_by_height_save_rest(self):
        self.remove_tmp_file(
            [
                "polygon-0x45dda9cb7c25131df268515131f647d726f50608-42447301-42448300.tmp.pkl",
                "polygon-0x45dda9cb7c25131df268515131f647d726f50608-42448301-42448799.tmp.pkl",
            ]
        )

        client = EthRpcClient(self.config["end_point"], "127.0.0.1:7890")
        files = self.query_3_save_2(client)
        print(files)
        self.assertTrue(len(files) == 2)

    def test_query_event_by_height_save_rest_again(self):
        self.remove_tmp_file(
            [
                "polygon-0x45dda9cb7c25131df268515131f647d726f50608-42447301-42448300.tmp.pkl",
                "polygon-0x45dda9cb7c25131df268515131f647d726f50608-42448301-42448799.tmp.pkl",
            ]
        )

        client = EthRpcClient(self.config["end_point"], "127.0.0.1:7890")
        files = self.query_3_save_2(client)
        print(files)
        self.assertTrue(len(files) == 2)
        # load from existing file again
        files = self.query_3_save_2(client)
        print(files)
        self.assertTrue(len(files) == 2)

    def query_3_save_2(self, client):
        return query_event_by_height(
            chain=typing.ChainType.polygon,
            client=client,
            contract_config=ContractConfig(
                "0x45dda9cb7c25131df268515131f647d726f50608",
                [constants.SWAP_KECCAK, constants.BURN_KECCAK, constants.COLLECT_KECCAK, constants.MINT_KECCAK],
            ),
            start_height=42447301,  # height difference cannot be divided by 2*500
            end_height=42448799,
            save_path=self.config["to_path"],
            save_every_query=2,
            batch_size=500,
            skip_timestamp=True,
        )

    def test_query_event_by_height_save_rest_remove_last(self):
        client = EthRpcClient(self.config["end_point"], "127.0.0.1:7890")
        files = self.query_3_save_2(client)
        # just remove the last file.
        self.remove_tmp_file(["polygon-0x45dda9cb7c25131df268515131f647d726f50608-42448301-42448799.tmp.pkl"])
        files = self.query_3_save_2(client)
        print(files)
        self.assertTrue(len(files) == 2)

    def test_query_event_by_height_save_rest_remove_first(self):
        client = EthRpcClient(self.config["end_point"], "127.0.0.1:7890")
        files = self.query_3_save_2(client)
        # just remove the first file.
        self.remove_tmp_file(["polygon-0x45dda9cb7c25131df268515131f647d726f50608-42447301-42448300.tmp.pkl"])
        files = self.query_3_save_2(client)
        print(files)
        self.assertTrue(len(files) == 2)

    def test_query_uniswap_pool_logs(self):
        files = query_uniswap_pool_logs(
            chain=typing.ChainType.polygon,
            pool_addr="0x45dda9cb7c25131df268515131f647d726f50608",
            end_point=self.config["end_point"],
            # start=date(2023, 5, 6),
            # end=date(2023, 5, 6),
            start_height=42353301,
            end_height=42393181,  # diff=39880
            save_path=self.config["to_path"],
            http_proxy="127.0.0.1:7890",
        )
        print(files)

    def test_append_proxy_file(self):
        append_proxy_log(
            raw_file_list=["../sample-data/polygon-0x45dda9cb7c25131df268515131f647d726f50608-2023-05-06.raw.csv"],
            start_height=42353301,
            end_height=42393181,
            chain=typing.ChainType.polygon,
            end_point=self.config["end_point"],
            save_path=self.config["to_path"],
            batch_size=500,
            http_proxy="127.0.0.1:7890",
            keep_tmp_files=True,
        )
