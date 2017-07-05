import os
import logging
import json
import math

from aiotg import Bot, chat
from database import db, text_search

greeting = """
    ✋ 歡迎來到棒棒勝 Music 的 Bot ! 🎧
輸入作者/曲名來搜尋音樂資料庫，傳送音樂檔案以增加至資料庫。
輸入 /help 來獲取說明!
** 丟進本 Bot 的音樂不會同步到頻道唷!只有頻道的會同步過來 owo **
"""

help = """
輸入作者/曲名來搜尋音樂資料庫。
輸入 /stats 來獲取 bot 資訊。
用 /music 指令來在群聊內使用棒棒勝 Music Bot，像這樣:
/music 棒棒勝

本 Bot 預設採用模糊搜尋，若要精準搜尋，請把關鍵字用引號括起來，像這樣:
"棒棒勝 Music"

本 Bot 也支援並排的嚴格搜尋來讓搜尋更加嚴格 (?):
"棒棒勝 Music" "Rex"
"""

not_found = """
找不到資料 :/
"""
bot = Bot(
    api_token=os.environ.get('API_TOKEN'),
    name=os.environ.get('BOT_NAME'),
    botan_token=os.environ.get("BOTAN_TOKEN")
)
logger = logging.getLogger("musicbot")
channel = bot.channel(os.environ.get('CHANNEL'))

@bot.handle("audio")
async def add_track(chat, audio):
    if (await db.tracks.find_one({ "file_id": audio["file_id"] })):
        await chat.send_text("資料庫裡已經有這首囉 owo")
        return

    if "title" not in audio:
        await chat.send_text("你丟的音樂沒有標題資訊唷 :(")
        return

    doc = audio.copy()
    try:
        if (chat.sender["id"]):
            doc["sender"] = chat.sender["id"]
    except:
        doc["sender"] = os.environ.get("CHANNEL")
        
    await db.tracks.insert(doc)
    if (str(chat.sender) == 'N/A'):
        sendervar = '棒棒勝 Music Channel'
    else:
        sendervar = str(chat.sender)
        logger.info("%s 新增了 %s %s", sendervar, doc.get("performer"), doc.get("title"))
        await chat.send_text(sendervar + " 新增了 " + str(doc.get("performer")) + " - " + str(doc.get("title")) + " !")


@bot.command(r'@%s (.+)' % bot.name)
@bot.command(r'/music@%s (.+)' % bot.name)
@bot.command(r'/music (.+)')
def music(chat, match):
    return search_tracks(chat, match.group(1))


@bot.command(r'\((\d+)/\d+\) 下一頁 "(.+)"')
def more(chat, match):
    page = int(match.group(1)) + 1
    return search_tracks(chat, match.group(2), page)


@bot.default
def default(chat, message):
        return search_tracks(chat, message["text"])


@bot.inline
async def inline(iq):
    logger.info("%s", str(iq.sender))
    logger.info("%s 搜尋了 %s", iq.sender, iq.query)
    cursor = text_search(iq.query)
    results = [inline_result(t) for t in await cursor.to_list(10)]
    await iq.answer(results)


@bot.command(r'/music(@%s)?$' % bot.name)
def usage(chat, match):
    return chat.send_text(greeting)


@bot.command(r'/start')
async def start(chat, match):
    tuid = chat.sender["id"]
    if not (await db.users.find_one({ "id": tuid })):
        logger.info("新用戶 %s", chat.sender)
        await db.users.insert(chat.sender.copy())

    await chat.send_text(greeting)


@bot.command(r'/stop')
async def stop(chat, match):
    tuid = chat.sender["id"]
    await db.users.remove({ "id": tuid })

    logger.info("%s quit", chat.sender)
    await chat.send_text("掰掰! 😢")


@bot.command(r'/help')
def usage(chat, match):
    return chat.send_text(help)


@bot.command(r'/stats')
async def stats(chat, match):
    count = await db.tracks.count()
    group = {
        "$group": {
            "_id": None,
            "size": {"$sum": "$file_size"}
        }
    }
    cursor = db.tracks.aggregate([group])
    aggr = await cursor.to_list(1)

    if len(aggr) == 0:
        return (await chat.send_text("統計資訊還沒好!"))

    size = human_size(aggr[0]["size"])
    text = '%d 首歌曲, %s' % (count, size)

    return (await chat.send_text(text))


def human_size(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    rank = int((math.log10(nbytes)) / 3)
    rank = min(rank, len(suffixes) - 1)
    human = nbytes / (1024.0 ** rank)
    f = ('%.2f' % human).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[rank])


def send_track(chat, keyboard, track):
    return chat.send_audio(
        audio=track["file_id"],
        title=track.get("title"),
        performer=track.get("performer"),
        duration=track.get("duration"),
        reply_markup=json.dumps(keyboard)
    )


async def search_tracks(chat, query, page=1):
    if(str(chat.sender) == "N/A"):
        pass
    else:
        logger.info("%s 搜尋了 %s", chat.sender, query)

        limit = 3
        offset = (page - 1) * limit

        cursor = text_search(query).skip(offset).limit(limit)
        count = await cursor.count()
        results = await cursor.to_list(limit)

        if count == 0:
            await chat.send_text(not_found)
            return

        # Return single result if we have exact match for title and performer
        if results[0]['score'] > 2:
            limit = 1
            results = results[:1]

        newoff = offset + limit
        show_more = count > newoff

        if show_more:
            pages = math.ceil(count / limit)
            kb = [['(%d/%d) 下一頁 "%s"' % (page, pages, query)]]
            keyboard = {
                "keyboard": kb,
                "resize_keyboard": True
            }
        else:
            keyboard = { "hide_keyboard": True }

        for track in results:
            await send_track(chat, keyboard, track)


def inline_result(track):
    return {
        "type": "audio",
        "id": track["file_id"],
        "audio_file_id": track["file_id"],
        "title": "{} - {}".format(
            track.get("performer", "未知的歌手"),
            track.get("title", "未命名標題")
        )
    }
