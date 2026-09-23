import requests
import json

def get_polymarket_eth_5m():
    url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&tag_slug=crypto&limit=200"
    try:
        res = requests.get(url, timeout=10).json()
        target = None
        for m in res:
            slug = m.get("slug", "").lower()
            if "eth" in slug and ("5m" in slug or "5-min" in slug or "5 minute" in slug):
                target = m
                break
        if not target:
            print("当前没有 ETH 5分钟盘口")
            return
        
        token_ids = json.loads(target.get("clobTokenIds", "[]"))
        if not token_ids:
            return

        question = target.get("question")
        token_id = token_ids[0]
        
        hist_url = f"https://clob.polymarket.com/prices-history?market={token_id}&interval=1h&fidelity=1"
        history = requests.get(hist_url, timeout=10).json().get("history", [])
        
        if len(history) < 20:
            print("数据不足，新盘口刚开")
            return

        klines = []
        curr_t = history[0]['t']
        chunk = []
        for item in history:
            if item['t'] - curr_t >= 300:
                if chunk:
                    p = [float(x['p']) for x in chunk]
                    klines.append({'high': max(p), 'low': min(p), 'close': p[-1]})
                curr_t = item['t']
                chunk = [item]
            else:
                chunk.append(item)
        if chunk:
            p = [float(x['p']) for x in chunk]
            klines.append({'high': max(p), 'low': min(p), 'close': p[-1]})

        if len(klines) >= 4:
            k1 = klines[-4]
            k2 = klines[-3]
            k3 = klines[-2]
            target_price = float(chunk[0]['p']) if chunk else 0.0
            
            print("========= 数据抓取成功 =========")
            print(f"【目标价 TWAP】: {target_price}")
            print(f"【第1根K线】最高: {k1['high']} | 最低: {k1['low']} | 收盘: {k1['close']}")
            print(f"【第2根K线】最高: {k2['high']} | 最低: {k2['low']} | 收盘: {k2['close']}")
            print(f"【第3根K线】最高: {k3['high']} | 最低: {k3['low']} | 收盘: {k3['close']}")
            print("================================")
            # 你的算法在这个下面自己写
        else:
            print("K线数据不够3根")
            
    except Exception as e:
        print(f"抓取报错: {e}")

if __name__ == "__main__":
    get_polymarket_eth_5m()
