import os
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
import re


client = AsyncIOMotorClient(host=os.environ.get('MONGO_HOST'))
db = client.python



def text_search(query):
    typel = query.split(" type:")
    if (query.find(">") == -1):

        query2 = typel[0].split(" ")
        if (len(typel) == 1):
            typef = 'audio'
        elif (typel[1] == 'mp3'):
            typef = 'mpeg'
        else:
            typef = typel[1]
        global textA
        textA = ''
        for k in range(len(query2)):
            global textA
            textA = textA + '(?=.*?' + query2[k] + ")"
        textA = textA + '.*?'
        final = re.compile (textA, re.IGNORECASE)
        return db.tracks.find(
            {"$and":[
                {'mime_type': {'$regex':typef, '$options':'i'}},
                {"$or":[
                    {'title': final},
                {'performer': final}
                ]}]},
            { 'score': { '$meta': 'textScore' } }).sort([('score', {'$meta': 'textScore'})])
    elif (query.find(">") != -1):
        art = typel[0].split(">")
        if (len(typel) == 1):
            typef = 'audio'
        elif (typel[1] == 'mp3'):
            typef = 'mpeg'
        else:
            typef = typel[1]
        aut2 = art[0].split(" ")
        global textAUT
        textAUT = ''
        for k in range(len(aut2)):
            global textAUT
            textAUT = textAUT + '(?=.*?' + aut2[k] + ")"
        textAUT = textAUT + '.*?'
        finalAUT = re.compile (textAUT, re.IGNORECASE)
        son2 = art[1].split(" ")
        global textSON
        textSON = ''
        for k in range(len(son2)):
            global textSON
            textSON = textSON + '(?=.*?' + son2[k] + ")"
        textSON = textSON + '.*?'
        finalSON = re.compile (textSON, re.IGNORECASE) 
        return db.tracks.find(
            {"$and":[
                {'mime_type': {'$regex':typef, '$options':'i'}},
                {"$and":[
                    {'title': finalSON},
                {'performer': finalAUT}
                ]}]},
            { 'score': { '$meta': 'textScore' } }).sort([('score', {'$meta': 'textScore'})])

async def prepare_index():
    await db.tracks.create_index([
        ("title", pymongo.TEXT),
        ("performer", pymongo.TEXT)
    ])
    await db.tracks.create_index([
        ("file_id", pymongo.ASCENDING)
    ])
    await db.users.create_index("id")
