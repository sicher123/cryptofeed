'''
Copyright (C) 2017-2020  Bryant Moscon - bmoscon@gmail.com
Please see the LICENSE file for the terms and conditions
associated with this software.
'''
# %%
import nest_asyncio 
nest_asyncio.apply()
from cryptofeed import FeedHandler
from cryptofeed.defines import KLINE
from cryptofeed.exchanges import HuobiR, HuobiDMR , HuobiSwapR , OKEx
from datetime import datetime

async def kline(**kwargs):
    data = kwargs["kline"]
    # print({k:type(v) for k, v in data.items()})
    print(f"KLine interest update: {kwargs}", datetime.now())


async def cb(**kwargs):
    pass

def main():
    fh = FeedHandler()

    # Add futures contracts
    pairs0 = ["BTC-USDT", "EOS-USDT"]
    pairs1 = ["BTC_CQ","EOS_CQ"]
    pairs2 = ["BTC-USD" , "EOS-USD"] 
    pairs3 = OKEx.get_active_symbols()[:5]
    print(pairs3)
    pair4 = ['XRP-USD-210326','LTC-USD-201225']
    # fh.add_feed(HuobiR(pairs=pairs0, channels=[KLINE], callbacks={KLINE: kline}))
    # fh.add_feed(HuobiDMR(pairs=pairs1, channels=[KLINE], callbacks={KLINE: kline}))
    # fh.add_feed(HuobiSwapR(pairs=pairs2, channels=[KLINE], callbacks={KLINE: kline}))
    fh.add_feed(OKEx(pairs=pairs3, channels=[KLINE], callbacks={KLINE: kline}))
    fh.run()

if __name__ == '__main__':
    main()

# %%
