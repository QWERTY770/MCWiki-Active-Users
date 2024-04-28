import os.path

from bs4 import BeautifulSoup
import requests
from time import sleep
import datetime

__author__ = "QWERTY770"
__version__ = "1.1"
__license__ = "MIT License"
end = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=+8)))
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


def main_group(groups: list[str]) -> str:
    li = ["系统管理员", "行政员", "界面管理员", "管理员", "巡查员", "机器人", "巡查豁免者"]
    for i in li:
        if i in groups:
            return i
    return ""


def get_wikitext(li: list) -> str:
    result = f"""{{| class="wikitable sortable collapsible"
|+ {start.year}年{start.month}月{start.day}日-{end.year}年{end.month}月{end.day}日活跃用户列表
|-
! 排名 !! 用户名 !! 操作数 !! 主用户组 !! 其他本地/全域/特殊用户组"""
    rank = pre_rank = 0
    pre = 0
    for data in li:
        rank += 1
        if data[1] != pre:
            pre_rank = rank
            pre = data[1]
        result += "\n|-\n"
        result += f"| {pre_rank} || [[User:{data[0]}|{data[0]}]] || {data[1]} ||"
        main = main_group(data[2])
        if main:
            result += f" [[Minecraft Wiki:{main}|{main}]]"
        else:
            result += " 无"
        result += " ||"
        for g in data[2]:
            if g != main:
                result += f" [[Minecraft Wiki:{g}|{g}]]"
    result += "\n|}"
    return result


if __name__ == "__main__":
    li = get_active_list()
    if not os.path.exists(f"data/{end.year}"):
        os.makedirs(f"data/{end.year}")
    with open(f"data/{end.year}/active-users-{end.strftime('%Y%m%d-%H%M%S')}.txt", "w", encoding="utf-8") as file:
        file.write(get_wikitext(li))
