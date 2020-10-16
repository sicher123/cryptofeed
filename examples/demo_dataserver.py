from cryptofeed import FeedHandler
from cryptofeed.defines import KLINE
from cryptofeed.exchanges import HuobiDMR, OKEx
from datetime import datetime, timedelta

# from cryptofeed.callback import BookCallback, TickerCallback, TradeCallback
# from cryptofeed.defines import BID, ASK, L2_BOOK, TICKER, TRADES, FUNDING, OPEN_INTEREST, KLINE


async def kline(**kwargs):
    data = kwargs["kline"]
    data["datetime"] = datetime.fromtimestamp(data["timestamp"])
    print(f"KLine data: {data}")

async def ok_kline(**kwargs):
    data = kwargs["data"]
    tick = data["candle"]
    # "2020-08-13T02:38:00.000Z" 转北京时间 + 8H   
    dt = datetime.strptime(tick.pop(0), "%Y-%m-%dT%H:%M:%S.000Z") + timedelta(hours=8)
    tick.append(dt)
    symbol = data["instrument_id"]
    
    # 初始是第二分钟
    # print(last_ticks[symbol][-1] + timedelta(minutes=1) , dt)
    if last_ticks[symbol][-1] + timedelta(minutes=1) == dt:
        # 取出lasttick数据输出，更新lasttick为下一分钟的最新数据
        bar_data = last_ticks[symbol]
        bar = {fields[i]: bar_data[i] for i in range(len(fields))}
        bar["count"] = 0
        await callback(bar, symbol, exchange)
        asyncio.sleep(0.1)
        last_ticks[symbol] = tick

    elif last_ticks[symbol][-1] == dt:
        last_ticks[symbol] = tick

def main():
    fh = FeedHandler()

    # Add futures contracts
    pairs = ["BTC_CQ","EOS_CQ"]
    fh.add_feed(HuobiDMR(pairs=pairs, channels=[KLINE], callbacks={KLINE: kline}))

    fh.run()

if __name__ == '__main__':
    main()