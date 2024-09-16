from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from pymongo import MongoClient

# Kết nối tới MongoDB
client = MongoClient('localhost', 27017)
db = client['dlubot_db']


class ActionSearchTransaction(Action):
    def name(self) -> Text:
        return "action_search_transaction"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        search_target = tracker.get_slot(key="search_target")
        transactions_collection = db['transactions']

        query_sults = transactions_collection.find({
            "$or": [
                {"Date": {"$regex": search_target, "$options": "i"}},       # Tìm trong trường Date
                {"Amount": int(search_target) if search_target.isdigit() else -1},  # Tìm theo Amount nếu search_target là số
                {"Content": {"$regex": search_target, "$options": "i"}},    # Tìm trong trường Content
                {"CT Code": float(search_target) if search_target.replace('.', '', 1).isdigit() else -1}  # Tìm theo CT Code nếu search_target là số thực
            ]
        }).limit(5)
        
        bot_response = ""
        for i in query_sults:
            bot_response += (
                f"DATE: {i['Date']}\n"
                f"AMOUNT: {str(i['Amount'])}\n"
                f"CONTENT: {i['Content']}\n"
                f"CT CODE: {str(i['CT Code'])}\n\n"  # Thêm dòng trống giữa các kết quả
            )
        
        dispatcher.utter_message(text = f"# Kết quả search với '{search_target}' #\n" + bot_response)
