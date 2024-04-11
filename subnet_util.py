import bittensor as bt
from bittensor.extrinsics.serving import get_metadata
from utils import functools, run_in_subprocess
from tqdm import tqdm
import concurrent.futures
import datetime
import typing
import time
import requests
from dataclasses import dataclass

SUBTENSOR = "finney"
NETUID = 10
METAGRAPH_RETRIES = 10
METAGRAPH_DELAY_SECS = 30

def get_subtensor_and_metagraph() -> typing.Tuple[bt.subtensor, bt.metagraph]:
    for i in range(0, METAGRAPH_RETRIES):
        try:
            print("Connecting to subtensor...")
            subtensor: bt.subtensor = bt.subtensor(SUBTENSOR)
            print("Pulling metagraph...")
            metagraph: bt.metagraph = subtensor.metagraph(NETUID, lite=False)
            return subtensor, metagraph
        except:
            if i == METAGRAPH_RETRIES - 1:
                raise
            print(
                f"Error connecting to subtensor or pulling metagraph, retry {i + 1} of {METAGRAPH_RETRIES} in {METAGRAPH_DELAY_SECS} seconds..."
            )
            time.sleep(METAGRAPH_DELAY_SECS)
    raise RuntimeError()

def get_tao_price() -> float:
    for i in range(0, METAGRAPH_RETRIES):
        try:
            return float(requests.get("https://api.mexc.com/api/v3/avgPrice?symbol=TAOUSDT").json()["price"])
        except:
            if i == METAGRAPH_RETRIES - 1:
                raise
            time.sleep(METAGRAPH_DELAY_SECS)
        raise RuntimeError()


@dataclass
class MinerData:
    uid: int
    hotkey: str
    block: int
    url: str
    incentive: float
    emission: float

    @classmethod
    def from_compressed_str(
        cls,
        uid: int,
        hotkey: str,
        block: int,
        cs:str,
        incentive: float,
        emission: float,
    ):
        """Returns an instance of this class from a compressed string representation"""
        tokens = cs.split(" ")
        return MinerData(
            uid=uid,
            hotkey=hotkey,
            block=block,
            url=tokens[0],
            incentive=incentive,
            emission=emission,
        )

def get_subnet_data(
    subtensor: bt.subtensor, metagraph: bt.metagraph
):

    # Function to be executed in a thread

    def fetch_data(uid):
        hotkey = metagraph.hotkeys[uid]
        try:
            partial = functools.partial(
                get_metadata, subtensor, metagraph.netuid, hotkey
            )
            metadata = run_in_subprocess(partial, 30)
        except Exception as e:
            return None

        if not metadata:
            return None
        commitment = metadata["info"]["fields"][0]
        hex_data = commitment[list(commitment.keys())[0]][2:]
        chain_str = bytes.fromhex(hex_data).decode()
        block = metadata["block"]
        incentive = metagraph.incentive[uid].nan_to_num().item()
        emission = (
            metagraph.emission[uid].nan_to_num().item() * 20
        )  # convert to daily TAO

        try:
            model_data = MinerData.from_compressed_str(
                uid, hotkey, block, chain_str, incentive, emission
            )
        except Exception as e:
            print(f"Error parsing model data for uid {uid}: {e}")
            return None
        print(model_data)
        return model_data

    # Use ThreadPoolExecutor to fetch data in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Prepare the list of futures
        futures = [executor.submit(fetch_data, uid) for uid in metagraph.uids.tolist()]
        
        for future in tqdm(
            concurrent.futures.as_completed(futures),
            desc="Metadata for hotkeys",
            total=len(futures),
        ):
            result = future.result()
            if result and result.url[0] != "{":
                results.append(result)

    return results

if __name__ == "__main__":
    (subtensor, metagraph) = get_subtensor_and_metagraph()
    data = get_subnet_data(subtensor, metagraph)
    print(data)
