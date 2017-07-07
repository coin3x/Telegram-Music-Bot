import os
import logging
import json
import math
import re

from aiotg import Bot, chat
from database import db, text_search

greeting = """
✋ 歡迎來到棒棒勝 Music 的 Bot ! 🎧
輸入關鍵字來搜尋音樂資料庫，傳送音樂檔案以增加至資料庫。
輸入 `/help` 來獲取說明!
** 丟進本 Bot 的音樂不會同步到頻道唷!只有頻道的會同步過來 owo **
"""

help = """
輸入關鍵字來搜尋音樂資料庫。
在關鍵字後輸入`type:TYPE`來限定音樂格式，像這樣:
```棒棒勝 type:flac```
```棒棒勝 type:mp3```
```棒棒勝 type:mpeg```
若同時想搜尋作者和曲名，請用 `>` 隔開 (預設為作者、曲名都納入搜尋)，像這樣:
```棒棒勝>洨安之歌```
也可以搭配`type`指令，像這樣:
```棒棒勝>洨安之歌 type:flac```
輸入 `/stats` 來獲取 bot 資訊。
用 `/music` 指令來在群聊內使用棒棒勝 Music Bot，像這樣:
```/music 棒棒勝```
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
    if (str(chat.sender) == 'N/A'):
        sendervar = '棒棒勝 Music Channel'
    else:
        sendervar = str(chat.sender)
    if (await db.tracks.find_one({ "file_id": audio["file_id"] })):
        await chat.send_text("資料庫裡已經有這首囉 owo")
        logger.info("%s 傳送了重複的歌曲 %s %s", sendervar, str(audio.get("performer")), str(audio.get("title")))
        await bot.send_message(os.environ.get("CHNID"),sendervar + " 傳送了重複的歌曲 " + str(audio.get("performer")) + " - " + str(audio.get("title")))
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
    logger.info("%s 新增了 %s %s", sendervar, doc.get("performer"), doc.get("title"))
    await bot.send_message(os.environ.get("CHNID"),sendervar + " 新增了 " + str(doc.get("performer")) + " - " + str(doc.get("title")))
    if (sendervar != '棒棒勝 Music Channel'):
        await chat.send_text(sendervar + " 新增了 " + str(doc.get("performer")) + " - " + str(doc.get("title")) + " !")


@bot.command(r'@%s (.+)' % bot.name)
@bot.command(r'/music@%s (.+)' % bot.name)
@bot.command(r'/music (.+)')
def music(chat, match):
    return search_tracks(chat, match.group(1))


@bot.command(r'\((\d+)/\d+\) 下一頁 "(.+)"')
def more(chat, match):
    page = int(match.group(1))
    return search_tracks(chat, match.group(2), page)


@bot.default
def default(chat, message):
    '''msg1 = message["text"].split(" type:")
    art = msg1[0].split('>')'''

    '''first= msg1[0].split(" ")
    global textA
    textA = ''
    for k in range(len(first)):
        textA = textA + '(?=.*?' + first[k] + ")"
    textA = textA + '.*?'
    final = re.compile (textA, re.IGNORECASE)
    logger.info(msg1[0])'''

    '''if (len(art) == 2):
        if (len(msg1) == 2):
            return search_tracks(chat, query=message["text"], author=art[0], song=art[1], typev=msg1[1])
        elif (len(msg1) == 1):
            return search_tracks(chat, query=message["text"], author=art[0], song=art[1])
    elif (len(msg1) == 2):
        return search_tracks(chat, message["text"], typev=msg1[1])
    elif (len(msg1) == 1):
        return search_tracks(chat, message["text"])'''
    return search_tracks(chat, message["text"])
    else:
        logger.info("元素個數有問題RR")
        bot.send_message(os.environ.get("CHNID"),"元素個數有問題RRR")
        bot.send_message(os.environ.get("CHNID"),'(message["text"] , msg1 , len(msg1) ) = ' + str(message["text"]) + " , " + str(msg1) + " , " + str(len(msg1)))
        logger.info('(message["text"] , msg1 , len(msg1)) = (%s , %s , %d)', str(message["text"]), str(msg1), len(msg1))

@bot.inline
async def inline(iq):
    msg = iq.query.split(" type:")
    art = msg[0].split('>')
    if (len(art) == 2):
        if (len(msg) == 2):
            logger.info("%s 搜尋了 %s 格式的 %s 的 %s", iq.sender, msg[1].upper(), art[0], art[1])
            await bot.send_message(os.environ.get("CHNID"),str(iq.sender) + " 搜尋了 " + msg[1].upper() + " 格式的 " + art[0] + "的" + art[1])
            cursor = text_search(typef=msg[1], aut=art[0], son=art[1])
            results = [inline_result(t) for t in await cursor.to_list(10)]
            await iq.answer(results)
        elif (len(msg) == 1):
            logger.info("%s 搜尋了 %s 的 %s", iq.sender,  art[0], art[1])
            await bot.send_message(os.environ.get("CHNID"),str(iq.sender) + " 搜尋了 " + art[0] + "的" + art[1])
            cursor = text_search(aut=art[0], son=art[1])
            results = [inline_result(t) for t in await cursor.to_list(10)]
            await iq.answer(results)
    elif (len(msg) == 2):
        logger.info("%s 搜尋了 %s 格式的 %s", iq.sender, msg[1].upper(), msg[0])
        await bot.send_message(os.environ.get("CHNID"),str(iq.sender) + " 搜尋了 " + msg[1].upper() + " 格式的 " + msg[0])
        cursor = text_search(msg[0], msg[1])
        results = [inline_result(t) for t in await cursor.to_list(10)]
        await iq.answer(results)
    elif (len(msg) == 1):
        logger.info("%s 搜尋了 %s", iq.sender, iq.query)
        await bot.send_message(os.environ.get("CHNID"),str(iq.sender) + " 搜尋了 " + str(iq.query))
        cursor = text_search(iq.query)
        results = [inline_result(t) for t in await cursor.to_list(10)]
        await iq.answer(results)
    else:
        logger.info("元素個數有問題RR")
        await bot.send_message(os.environ.get("CHNID"),"元素個數有問題RRR")
        await bot.send_message(os.environ.get("CHNID"),"(iq.query , msg , len(msg)) = " + str(iq.query) + " , " + str(msg) + " , " + str(len(msg)))
        logger.info("(iq.query , msg , len(msg)) = (%s , %s , %d)", str(iq.query), str(msg), len(msg))


@bot.command(r'/music(@%s)?$' % bot.name)
def usage(chat, match):
    return chat.send_text(greeting)


@bot.command(r'/start')
async def start(chat, match):
    tuid = chat.sender["id"]
    if not (await db.users.find_one({ "id": tuid })):
        logger.info("新用戶 %s", chat.sender)
        await bot.send_message(os.environ.get("CHNID"),"新用戶 " + str(chat.sender))
        await db.users.insert(chat.sender.copy())

    await chat.send_text(greeting)


@bot.command(r'/stop')
async def stop(chat, match):
    tuid = chat.sender["id"]
    await db.users.remove({ "id": tuid })

    logger.info("%s 退出了", chat.sender)
    await bot.send_message(os.environ.get("CHNID"),str(chat.sender) + " 退出了")
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


'''async def search_tracks(chat, query=1, page=1, typev='audio', author=1, song=1):'''
async def search_tracks(chat, query, page=1):
    if(str(chat.sender) != "N/A"):
        typel = query.split(" type:")
        if (query.find(">") != -1):
            if (typel[1] == 'audio'):
                art = query.split('>')
                author = art[0]
                song = art[1]
                logger.info("%s 搜尋了 %s 的 %s", chat.sender, author, song)
                await bot.send_message(os.environ.get("CHNID"),str(chat.sender) + " 搜尋了 " + author + " 的 " + song)
            else:
                art = type1[0].split('>')
                query = type1[0]
                author = art[0]
                song = art[1]
                logger.info("%s 搜尋了 %s 格式的 %s 的 %s", chat.sender, typel[1].upper(), author, song)
                await bot.send_message(os.environ.get("CHNID"),str(chat.sender) + " 搜尋了 " + typel[1].upper() + " 格式的 " + author + " 的 " + song)
        elif (typev == 'audio'):
            logger.info("%s 搜尋了 %s", chat.sender, query)
            await bot.send_message(os.environ.get("CHNID"),str(chat.sender) + " 搜尋了 " + str(query))
        else:
            logger.info("%s 搜尋了 %s 格式的 %s", chat.sender, typel[1].upper(), type1[0])
            await bot.send_message(os.environ.get("CHNID"),str(chat.sender) + " 搜尋了 " + typel[1].upper() + " 格式的 " + str(type1[0]))

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
            kb = [['(%d/%d) 下一頁 "%s"' % (page+1, pages, query)]]
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
