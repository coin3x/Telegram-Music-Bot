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

'''def text_search(query,typef='audio',aut=1,son=1):'''
def text_search(query):
    typel = query.split(" type:")
    typef = typel[1]
    if (query.find(">") == -1):
        '''queryty = query.split(" type:")'''
        query2 = typel[0].split(" ")
        typef = typel[1]
        if (len(querty) == 1):
            typef = 'audio'
        elif (typef == 'mp3'):
            typef = 'mpeg'
        else:
            typef = typel[1]
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
        art = typel[0].split(">")
        typef = typel[1]
        if (len(typel) == 1):
            typef = 'audio'
        elif (typef != 'mp3'):
            typef = 'mpeg'
        else:
            typef = typel[1]
        aut2 = art[0].split(" ")
        textAUT = ''
        for k in range(len(aut2)):
            textAUT = textAUT + '(?=.*?' + aut2[k] + ")"
        textAUT = textAUT + '.*?'
        logger.info(textAUT)
        finalAUT = re.compile (textAUT, re.IGNORECASE)
        son2 = art[1].split(" ")
        textSON = ''
        for k in range(len(son2)):
            textSON = textSON + '(?=.*?' + son2[k] + ")"
        textSON = textSON + '.*?'
        logger.info(textSON)
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
