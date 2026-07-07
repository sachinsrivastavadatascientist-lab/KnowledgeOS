from datetime import datetime
from mongodb.connection import db
from pymongo.errors import DuplicateKeyError

class MongoManager:

    def __init__(self):

        self.sessions = db["sessions"]

        self.sessions.create_index(
            "session_id",
            unique=True
        )

        self.sessions.create_index(
            [("user_id",1),("session_id",1)]
        )

        self.sessions.create_index(
            "created_at",
            expireAfterSeconds=30*24*60*60
        )

    ########################################################

    def save_session(
        self,
        session_id:str,
        user_id:str,
        faiss_path:str
    ):

        data={
            "session_id":session_id,
            "user_id":user_id,
            "faiss_path":faiss_path,
            "created_at":datetime.utcnow(),
            "last_accessed":datetime.utcnow(),
            "status":"active"
        }

        try:

            self.sessions.insert_one(data)

        except DuplicateKeyError:

            raise Exception("Session already exists")

    ########################################################

    def get_session(
        self,
        session_id:str,
        user_id:str
    ):

        return self.sessions.find_one(

            {
                "session_id":session_id,
                "user_id":user_id
            }

        )

    ########################################################

    def update_last_access(
        self,
        session_id:str
    ):

        self.sessions.update_one(

            {
                "session_id":session_id
            },

            {
                "$set":
                {
                    "last_accessed":datetime.utcnow()
                }
            }

        )

    ########################################################

    def delete_session(
        self,
        session_id:str
    ):

        self.sessions.delete_one(

            {
                "session_id":session_id
            }

        )

    ########################################################

    def get_all_sessions(
        self,
        user_id:str
    ):

        return list(

            self.sessions.find(

                {
                    "user_id":user_id
                },

                {
                    "_id":0
                }

            )

        )