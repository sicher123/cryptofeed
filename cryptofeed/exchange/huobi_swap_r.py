import time
import json
import aiohttp
import asyncio
import requests
# from decimal import Decimal
from datetime import datetime 

from cryptofeed.feed import RestFeed
from cryptofeed.defines import KLINE , HUOBI_SWAP_R
from cryptofeed.standards import pair_exchange_to_std, timestamp_normalize


def get_exchange_ts():
    url = "https://api.huobi.pro/v1/common/timestamp"

    try:
        res = requests.get(url).json()
    except:
        raise ConnectionError("请检查网络连接及vpn是否正常，或交易所数据维护")

    if res.get("status") == "ok":
        return res.get("data")/1000
        # return datetime.fromtimestamp(res.get("data")/1000)
    else:
        return False

def get_delay():
    '''
    包含网络传输时间的延迟
    '''
    exchange_ts = get_exchange_ts()
    ts = time.time()
    delay =  ts - exchange_ts
    return delay
    # print(ts, exchange_ts, delay)

def get_signal(delay, start=0.1, end=3):
    now_ts = time.time()
    value = end - 0.1

    if delay > 0 and delay < value:
        expect_ts = now_ts - delay

    elif abs(delay) >= value:
        print(f"error : delay>{value}s, can't get data")
        expect_ts = now_ts
    else:
        expect_ts = now_ts
        
    dt = datetime.fromtimestamp(expect_ts)

    if dt.second >= start and dt.second <= end:
        return True
    else:
        return False


class HuobiSwapR(RestFeed):
    id = HUOBI_SWAP_R

    def __init__(self, pairs=None, channels=None, callbacks=None, config=None, **kwargs):
        super().__init__('https://api.hbdm.com/swap-ex/market/history/kline', pairs=pairs, channels=channels, config=config, callbacks=callbacks, **kwargs)
        self.delay = None

    def __reset(self):
        self.last_trade_update = {}

    async def _kline(self, signal, session, pair):
        if signal:
            url = f"{self.address}?period=1min&size=2&contract_code={pair}"
            
            async with session.get(url) as response:
                text = await response.text()
                res = json.loads(text)

                if res.get("status") == "ok":
                    data = res["data"][0]
                    data["datetime"] = datetime.fromtimestamp(data["id"])

                    ori_pair = self.anti_pairs.get(pair)
                    await self.callback(KLINE,
                            feed=self.id,
                            pair=ori_pair,
                            kline=data,
                            timestamp=timestamp_normalize(self.id, data['id']))
                    
                    # await self.callback(KLINE,
                    #         feed=self.id,
                    #         pair=pair,
                    #         # start=kline['start'],
                    #         # end=kline['end'],
                    #         open=Decimal(data["open"]),
                    #         close=Decimal(data["close"]),
                    #         high=Decimal(data["high"]),
                    #         low=Decimal(data["low"]),
                    #         volume=Decimal(data["vol"]),
                    #         amount=Decimal(data["amount"]),
                    #         timestamp=timestamp_normalize(self.id, data['id'])
                    #         )
            await asyncio.sleep(40)

    async def subscribe(self):
        self.__reset()
        return

    async def message_handler(self):
        if not self.delay:
            self.delay = get_delay()

        signal = get_signal(self.delay)
        
        if signal:
            self.delay = None

        async def handle(session, pair, chan):
            if chan == KLINE:
                await self._kline(signal, session, pair)
            # We can do 15 requests a second
            await asyncio.sleep(0.07)

        tasks = [] 
        async with aiohttp.ClientSession() as session:
            if self.config:
                for chan in self.config:
                    for pair in self.config[chan]:
                        tasks.append(handle(session, pair, chan))
            else:
                for chan in self.channels:
                    for pair in self.pairs:
                        tasks.append(handle(session, pair, chan))

            await asyncio.gather(*tasks)