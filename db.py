from pymongo import MongoClient


class DB:
    """
    THis DB class manage all the operations related to MongoDB
    """

    def __init__(self, database="SEARCH", collection="test"):
        """
       Initialize a website
        """
        self.client = MongoClient()
        self.db = self.client[database]
        self.collection = self.db[collection]

    def addSiteOne(self, entry):
        self.collection.insert_one(entry)
        #print("Insert one entry. ")

    def updateSiteOne(self, entry):
        self.collection.update_one(
            {"_id": entry["_id"]}, {"$set": entry}, True)
        #print("Insert one entry. ")
