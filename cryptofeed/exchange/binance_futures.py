'''
Copyright (C) 2017-2020  Bryant Moscon - bmoscon@gmail.com

Please see the LICENSE file for the terms and conditions
associated with this software.
'''
from decimal import Decimal
import logging

from yapic import json

from cryptofeed.defines import BINANCE_FUTURES, OPEN_INTEREST, TICKER, KLINE
from cryptofeed.exchange.binance import Binance
from cryptofeed.standards import pair_exchange_to_std, timestamp_normalize
from cryptofeed.pairs import gen_anti_pairs
from datetime import datetime

LOG = logging.getLogger('feedhandler')


class BinanceFutures(Binance):
    id = BINANCE_FUTURES

    def __init__(self, pairs=None, channels=None, callbacks=None, depth=1000, **kwargs):
        super().__init__(pairs=pairs, channels=channels, callbacks=callbacks, depth=depth, **kwargs)
        self.ws_endpoint = 'wss://fstream.binance.com'
        self.rest_endpoint = 'https://fapi.binance.com/fapi/v1'
        period = kwargs.get("period")
        if not period:
            period = "1m"        
        self.period = period
        self.address = self._address()

    def _address(self):
        address = self.ws_endpoint + '/stream?streams='
        for chan in self.channels if not self.config else self.config:
            if chan == OPEN_INTEREST:
                continue
            for pair in self.pairs if not self.config else self.config[chan]:
                pair = pair.lower()
                if chan == TICKER:
                    stream = f"{pair}@bookTicker/"
                elif chan == KLINE:
                    stream = f"{pair}@{chan}_{self.period}/" 
                else:
                    stream = f"{pair}@{chan}/"
                address += stream
        if address == f"{self.ws_endpoint}/stream?streams=":
            return None
        return address[:-1]

    def _check_update_id(self, pair: str, msg: dict) -> (bool, bool):
        skip_update = False
        forced = not self.forced[pair]

        if forced and msg['u'] < self.last_update_id[pair]:
            skip_update = True
        elif forced and msg['U'] <= self.last_update_id[pair] <= msg['u']:
            self.last_update_id[pair] = msg['u']
            self.forced[pair] = True
        elif not forced and self.last_update_id[pair] == msg['pu']:
            self.last_update_id[pair] = msg['u']
        else:
            self._reset()
            LOG.warning("%s: Missing book update detected, resetting book", self.id)
            skip_update = True
        return skip_update, forced

    async def _kline(self, msg: dict, timestamp: float):
        pair = msg.get("s")
        kline = msg.get("k")
        is_finish = kline.get("x")

        if is_finish:
            update_timestamp = timestamp_normalize(self.id, kline.get("t"))
                
            kline_dict  =  {"open": kline.get("o"),
                            "high": kline.get("h"),
                            "low": kline.get("l"),
                            "close": kline.get("c"),
                            "vol": kline.get("v"),
                            "amount": kline.get("q"),
                            "datetime": datetime.fromtimestamp(update_timestamp)}

            await self.callback(KLINE,
                                feed=self.id,
                                pair=pair,
                                kline=kline_dict,
                                timestamp=update_timestamp
                                )

    async def message_handler(self, msg: str, timestamp: float):
        msg = json.loads(msg, parse_float=Decimal)

        # Combined stream events are wrapped as follows: {"stream":"<streamName>","data":<rawPayload>}
        # streamName is of format <symbol>@<channel>
        pair, _ = msg['stream'].split('@', 1)
        msg = msg['data']

        pair = pair.upper()

        msg_type = msg.get('e')
        if msg_type is None:
            # For the BinanceFutures API it appears
            # the ticker stream (<symbol>@bookTicker) is
            # the only payload without an "e" key describing the event type
            await self._ticker(msg, timestamp)
        elif msg_type == 'depthUpdate':
            await self._book(msg, pair, timestamp)
        elif msg_type == 'aggTrade':
            await self._trade(msg, timestamp)
        elif msg_type == 'forceOrder':
            await self._liquidations(msg, timestamp)
        elif msg_type == 'markPriceUpdate':
            await self._funding(msg, timestamp)
        elif msg_type == 'kline':
            await self._kline(msg, timestamp)
        else:
            LOG.warning("%s: Unexpected message received: %s", self.id, msg)