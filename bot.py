import os
import discord
import requests
import asyncio

# --- 設定 ---
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN が見つかりません。Renderに環境変数を設定してください。")

CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
if CHANNEL_ID == 0:
    raise ValueError("CHANNEL_ID が見つかりません。Renderに環境変数を設定してください。")

API_URL = "https://api.dexscreener.com/latest/dex/pairs/osmosis/1943"
CHECK_INTERVAL = 300  # チェック間隔（秒）
PRICE_CHANGE_THRESHOLD = 0.0025  # 0.25%以上の変動で通知

# --- BOT 初期化 ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)

previous_price = None

@client.event
async def on_ready():
    print(f"✅ ログイン完了: {client.user}")
    await monitor_price()

async def monitor_price():
    global previous_price
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("❌ チャンネルが見つかりません。CHANNEL_IDを確認してください。")
        return

    while not client.is_closed():
        try:
            response = requests.get(API_URL, timeout=10)
            data = response.json()
            current_price = float(data["pair"]["priceUsd"])

            if previous_price:
                change_ratio = (current_price - previous_price) / previous_price
                if abs(change_ratio) >= PRICE_CHANGE_THRESHOLD:
                    direction = "📈 上昇" if change_ratio > 0 else "📉 下落"
                    percentage = round(change_ratio * 100, 2)
                    await channel.send(
                        f"{direction} アラート！\n"
                        f"価格が {percentage}% 変動しました。\n"
                        f"現在価格: ${current_price:.4f}（前回: ${previous_price:.4f}）"
                    )

            previous_price = current_price
        except Exception as e:
            print(f"⚠ エラー発生: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

client.run(TOKEN)
