import datetime

from umongo import Document, fields

from .common import instance
from .plant import Plant


@instance.register
class User(Document):
    name = fields.StrField(required=True)
    email = fields.EmailField(required=True)
    verification_code = fields.IntField(allow_none=True)
    password = fields.StrField(required=True)
    plants = fields.ListField(fields.ReferenceField(Plant), allow_none=True)
    is_verified = fields.BoolField(default=False)
    created_at = fields.DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        collection_name = "users"

    async def get_dict(self):
        d = self.to_mongo()
        d["id"] = str(d["_id"])
        del d["_id"]
        del d["verification_code"]
        del d["password"]
        if d.get("plants"):
            d["plants"] = [str(plant) for plant in d["plants"]]
        else:
            d["plants"] = []
        return d