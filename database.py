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

def text_search(query,typef='audio'):
    if (typef == 'mp3'):
        typef = 'mpeg'
    query2 = query.split(" ")
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


async def prepare_index():
    await db.tracks.create_index([
        ("title", pymongo.TEXT),
        ("performer", pymongo.TEXT)
    ])
    await db.tracks.create_index([
        ("file_id", pymongo.ASCENDING)
    ])
    await db.users.create_index("id")
