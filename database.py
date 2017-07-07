import os
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient


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
    return db.tracks.find(
        {"$and":[
            {'mime_type': {'$regex':typef, '$options':'i'}},
            {"$or":[
                {'title': {"$in": query}},
                {'performer': {"$in": query}}
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
