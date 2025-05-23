import peewee

db = peewee.SqliteDatabase("search_history.db")


class SearchHistory(peewee.Model):
    date = peewee.DateTimeField()
    title = peewee.CharField()
    description = peewee.TextField(null=True)
    rating = peewee.FloatField()
    year = peewee.IntegerField()
    genres = peewee.CharField()
    age_rating = peewee.CharField(max_length=10, null=True)
    poster = peewee.CharField(null=True)
    budget = peewee.CharField()

    class Meta:
        database = db


db.connect()
db.create_tables([SearchHistory], safe=True)
