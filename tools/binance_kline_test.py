import argparse
import asyncio
import zlib
import websockets
import json
from collections import namedtuple

RestUrl = namedtuple("url", ["base_url", "type", "symbol", "size"])

url = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
sub = {
        "method": "SUBSCRIBE",
        "params":
        [
        "btcusdt@kline_1m"
        ],
        "id": 1
        }

# sub = {}
# parser = argparse.ArgumentParser()
# parser.add_argument('--count', default=3, type=int, help='Number of messages to receive before exiting')
# parser.add_argument('-z', action='store_true', help='Use gzip on messages')
# args = parser.parse_args()

def listen():
    pass

async def main():
    async with websockets.connect(url) as websocket:
        sub_string = json.dumps(sub)
        await websocket.send(sub_string)
        print(f"subscribe > {sub_string}")

        while True:
            response = await websocket.recv()
            print (json.loads(response))
            print(f"< {response}")
            # if not is_gzip:
            #     print(f"< {response}")
            # else:
            #     print(f"< {zlib.decompress(response, 16+zlib.MAX_WBITS)}")

asyncio.get_event_loop().run_until_complete(main())

'''
{
  "e": "kline",     // 事件类型
  "E": 123456789,   // 事件时间
  "s": "BNBBTC",    // 交易对
  "k": {
    "t": 123400000, // 这根K线的起始时间
    "T": 123460000, // 这根K线的结束时间
    "s": "BNBBTC",  // 交易对
    "i": "1m",      // K线间隔
    "f": 100,       // 这根K线期间第一笔成交ID
    "L": 200,       // 这根K线期间末一笔成交ID
    "o": "0.0010",  // 这根K线期间第一笔成交价
    "c": "0.0020",  // 这根K线期间末一笔成交价
    "h": "0.0025",  // 这根K线期间最高成交价
    "l": "0.0015",  // 这根K线期间最低成交价
    "v": "1000",    // 这根K线期间成交量
    "n": 100,       // 这根K线期间成交笔数
    "x": false,     // 这根K线是否完结(是否已经开始下一根K线)
    "q": "1.0000",  // 这根K线期间成交额
    "V": "500",     // 主动买入的成交量
    "Q": "0.500",   // 主动买入的成交额
    "B": "123456"   // 忽略此参数
  }
}
'''