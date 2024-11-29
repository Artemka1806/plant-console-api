import datetime

from umongo import Document, fields

from .common import instance


@instance.register
class Plant(Document):
    code  = fields.StrField(required=True)
    name = fields.StrField(allow_none=True)
    points = fields.IntField(default=0)
    level = fields.IntField(default=0)
    money = fields.IntField(default=0)
    last_watered_at = fields.DateTimeField(allow_none=True)
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        collection_name = "plants"
    
    async def get_dict(self):
        d = self.to_mongo()
        d["id"] = str(d["_id"])
        del d["_id"]
        return d