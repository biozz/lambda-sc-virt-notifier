import os

import pickledb
import requests
from bs4 import BeautifulSoup

ORDER_ID = os.getenv("ORDER_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
USER_AGENT = os.getenv("USER_AGENT")


def main():
    db = pickledb.load("state.db", auto_dump=True)
    order_page_response = requests.get(
        f"https://sc-virt.ru/stats_remont/?id={ORDER_ID}&num=nz&sub=",
        headers={
            "User-Agent": USER_AGENT,
        },
    )
    html_data = order_page_response.content
    soup = BeautifulSoup(html_data, "html.parser")
    order_info = soup.find("div", {"id": "content"}).find("p").text
    order_status = soup.find("div", {"id": "content"}).find_all("td")[-1].text
    if db.get("status") == order_status:
        # nothing changed, exit
        return
    # status changed, store and notify
    db.set("status", order_status)
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": f"{order_info}: {order_status}"},
    )


if __name__ == "__main__":
    main()
