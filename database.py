import os
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
import re


client = AsyncIOMotorClient(host=os.environ.get('MONGO_HOST'))
db = client.python


'''def text_search(query):
    return db.tracks.find(
        {"$or":[
            {'title':{'$regex':query, '$options':'i'}},
            {'performer':{'$regex':query, '$options':'i'}}
        ]},
        { 'score': { '$meta': 'textScore' } }
    ).sort([('score', {'$meta': 'textScore'})])'''

def text_search(query,typef='audio',aut=1,son=1):
    if (typef == 'mp3'):
        typef = 'mpeg'
    if (query.find(">") == -1):
        queryty = query.split(" type:")
        query2 = queryty.split(" ")
        if (len(querty) == 1):
            typef = 'audio'
        else:
            typef = querty[1]
        global textA
        textA = ''
        for k in range(len(query2)):
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
        RRR = query.split(" type:")
        art = RRR[0].split(">")
        if (len(RRR) == 1):
            typef = 'audio'
        else:
            typef = RRR[1]
        aut = art[0]
        son = art[1]
        aut2 = aut.split(" ")
        global textAUT
        textAUT = ''
        for k in range(len(aut2)):
            textAUT = textAUT + '(?=.*?' + aut2[k] + ")"
        textAUT = textAUT + '.*?'
        finalAUT = re.compile (textAUT, re.IGNORECASE)
        son2 = son.split(" ")
        global textSON
        textSON = ''
        for k in range(len(son2)):
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
