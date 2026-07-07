from datetime import datetime
import uuid

from mongodb.mongo_manager import MongoManager


class SessionManager:

    def __init__(self):
        self.mongo = MongoManager()

    ########################################################

    def generate_session_id(
        self,
        user_id: str
    ) -> str:
        """
        Example:

        session_sachin_20260705_193055_a8f3c1d2
        """

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        unique = str(uuid.uuid4())[:8]

        return f"session_{user_id}_{timestamp}_{unique}"

    ########################################################

    def create_session(
        self,
        session_id: str,
        user_id: str,
        faiss_path: str
    ):

        # session_id = self.generate_session_id(user_id)   # backend/api me pehle hi generate ho chuka hai

        self.mongo.save_session(
            session_id=session_id,
            user_id=user_id,
            faiss_path=faiss_path
        )

        return session_id

    ########################################################

    def get_session(
        self,
        session_id: str,
        user_id: str
    ):

        session = self.mongo.get_session(
            session_id=session_id,
            user_id=user_id
        )

        return session

    ########################################################

    def touch_session(
        self,
        session_id: str
    ):

        self.mongo.update_last_access(
            session_id=session_id
        )

    ########################################################

    def delete_session(
        self,
        session_id: str
    ):

        self.mongo.delete_session(
            session_id=session_id
        )

    ########################################################

    def get_user_sessions(
        self,
        user_id: str
    ):

        return self.mongo.get_all_sessions(
            user_id=user_id
        )