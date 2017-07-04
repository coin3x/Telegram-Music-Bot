import os
import pymongo

from motor.motor_asyncio import AsyncIOMotorClient


client = AsyncIOMotorClient(host="mongodb://$OPENSHIFT_MONGODB_DB_HOST:$OPENSHIFT_MONGODB_DB_PORT/")
db = client.python


def text_search(query):
    return db.tracks.find(
        {"$or":[
            {'title':{'$regex':query, '$options':'i'}},
            {'performer':{'$regex':query, '$options':'i'}}
        ]},
        { 'score': { '$meta': 'textScore' } }
    ).sort([('score', {'$meta': 'textScore'})])


async def prepare_index():
    await db.tracks.create_index([
        ("title", pymongo.TEXT),
        ("performer", pymongo.TEXT)
    ])
    await db.tracks.create_index([
        ("file_id", pymongo.ASCENDING)
    ])
    await db.users.create_index("id")
