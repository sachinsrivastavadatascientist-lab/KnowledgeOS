from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from mongodb.connection import db


class HistoryManager:

    def __init__(self):

        self.history = db["chat_history"]

        self.history.create_index(
            [("session_id", 1), ("user_id", 1)],
            unique=True
        )

    ########################################################

    def load_history(
        self,
        session_id: str,
        user_id: str
    ) -> ChatMessageHistory:

        chat_history = ChatMessageHistory()

        data = self.history.find_one(
            {
                "session_id": session_id,
                "user_id": user_id
            }
        )

        if data is None:
            return chat_history

        for msg in data["messages"]:

            if msg["role"] == "human":

                chat_history.add_message(
                    HumanMessage(content=msg["content"])
                )

            else:

                chat_history.add_message(
                    AIMessage(content=msg["content"])
                )

        return chat_history

    ########################################################

    def save_history(
        self,
        session_id: str,
        user_id: str,
        history: ChatMessageHistory
    ):

    ######### code for debugging########3
        print("="*50)
        print("SAVE HISTORY CALLED")
        print(history.messages)
        print("="*50)

        messages = []

        for msg in history.messages:

            if isinstance(msg, HumanMessage):

                role = "human"

            else:

                role = "ai"

            messages.append(
                {
                    "role": role,
                    "content": msg.content
                }
            )

        self.history.update_one(

            {
                "session_id": session_id,
                "user_id": user_id
            },

            {
                "$set":
                {
                    "messages": messages
                }
            },

            upsert=True

        )

    ########################################################

    def clear_history(
        self,
        session_id: str,
        user_id: str
    ):

        self.history.delete_one(

            {
                "session_id": session_id,
                "user_id": user_id
            }

        )