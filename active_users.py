import os.path

from bs4 import BeautifulSoup
import requests
from time import sleep
import datetime

__author__ = "QWERTY770"
__version__ = "1.0"
__license__ = "MIT License"
end = datetime.datetime.now()
start = end - datetime.timedelta(days=30)
url = "https://zh.minecraft.wiki/w/Special:%E6%B4%BB%E8%B7%83%E7%94%A8%E6%88%B7?username="


def get_active_list() -> list:
    last_user = ""
    get = 1
    result = []
    while get:
        req = requests.get(url + last_user, timeout=20)
        if req.status_code != 200:
            print(f"Failed to get active users list, code = {req.status_code}")
            sleep(5)
            return get_active_list()
        soup = BeautifulSoup(req.text, 'html.parser')
        li = soup.find_all("li")
        get = 0
        for data in li:
            if data.select(".mw-userlink"):
                link = data.findAll("a")
                user = link[0].bdi.contents[0]
                if user == last_user:
                    continue
                edits = data.contents[-1]
                edits = edits.split("过去30天有")[1].split("次操作")[0]
                group = []
                if len(link) >= 4:
                    for i in range(3, len(link)):
                        group.append(link[i].contents[0])
                print(user, edits, group)
                result.append([user, edits, group])
                get += 1
        last_user = result[-1][0]
    result.sort(key=lambda x: int(x[1].replace(",", "")), reverse=True)
    return result


def get_wikitext(li: list) -> str:
    result = f"""{{| class="wikitable sortable collapsible"
|+ {start.year}年{start.month}月{start.day}日-{end.year}年{end.month}月{end.day}日活跃用户列表
|-
! 排名 !! 用户名 !! 操作数 !! 本地/特殊用户组"""
    rank = pre_rank = 0
    pre = 0
    for data in li:
        rank += 1
        if data[1] != pre:
            pre_rank = rank
            pre = data[1]
        result += "\n|-\n"
        result += f"| {pre_rank} || [[User:{data[0]}|{data[0]}]] || {data[1]} ||"
        for g in data[2]:
            result += f" [[Minecraft Wiki:{g}|{g}]]"
        if len(data[2]) == 0:
            result += " 无"
    result += "\n|}"
    return result


if __name__ == "__main__":
    li = get_active_list()
    if not os.path.exists(f"data/{end.year}"):
        os.makedirs(f"data/{end.year}")
    with open(f"data/{end.year}/active-users-{end.strftime('%Y%m%d-%H%M%S')}.txt", "w", encoding="utf-8") as file:
        file.write(get_wikitext(li))
