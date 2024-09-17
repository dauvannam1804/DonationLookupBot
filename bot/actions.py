from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from pymongo import MongoClient
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')  # Sử dụng backend không tương tác

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
                {"Date": {"$regex": search_target, "$options": "i"}},
                {"Amount": int(search_target) if search_target.isdigit() else -1},
                {"Content": {"$regex": search_target, "$options": "i"}},
                {"CT Code": float(search_target) if search_target.replace('.', '', 1).isdigit() else -1}
            ]
        }).limit(5)
        
        bot_response = ""
        for i in query_sults:
            bot_response += (
                f"DATE: {i['Date']}\n"
                f"AMOUNT: {str(i['Amount'])}\n"
                f"CONTENT: {i['Content']}\n"
                f"CT CODE: {str(i['CT Code'])}\n\n"
            )
        
        dispatcher.utter_message(text = f"# Kết quả search với '{search_target}' #\n" + bot_response)


class ActionCalculateTotalDonationsWithinDateRange(Action):
    def name(self) -> Text:
        return "action_calculate_total_donations_within_date_range"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        donation_timeframe = tracker.get_slot(key='donation_timeframe')
        transactions_collection = db['transactions']
        timeframe_parts = donation_timeframe.split()

        if len(timeframe_parts) == 1:
            start_date = timeframe_parts[0]
            end_date = start_date
        else:
            start_date = timeframe_parts[0]
            end_date = timeframe_parts[1]

        query = [
            {
                "$match": {
                    "Date": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_amount": {"$sum": "$Amount"}
                }
            }
        ]    
        result = list(transactions_collection.aggregate(query))

        if result:
            total_amount = result[0]['total_amount']
            if len(timeframe_parts) == 1:
                dispatcher.utter_message(text = f"Tổng số tiền ủng hộ trong ngày {start_date} là {total_amount} vnd")
            else:
                dispatcher.utter_message(text = f"Tổng số tiền ủng hộ trong khoảng thời gian {start_date}-{end_date} là {total_amount} vnd")
        else:
            dispatcher.utter_message(text="Không có giao dịch nào trong khoảng thời gian này.")


class ActionDrawTransactionChartWithinDateRange(Action):
    def name(self) -> Text:
        return "action_draw_transaction_chart_within_date_range"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        donation_timeframe = tracker.get_slot(key='transaction_date_range')
        transactions_collection = db['transactions']

        start_date, end_date = donation_timeframe.split()
        query = [
            {
                "$match": {
                    "Date": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": "$Date",
                    "transaction_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        result = list(transactions_collection.aggregate(query))
        dates = [entry["_id"] for entry in result]
        transaction_counts = [entry["transaction_count"] for entry in result]

        plt.figure(figsize=(10, 6))
        plt.plot(dates, transaction_counts, marker="o", linestyle="-", color="b")

        for i, count in enumerate(transaction_counts):
            plt.text(dates[i], count + 3000, str(count), ha='right', fontsize=10, color='black')

        plt.title("Số lượng giao dịch theo ngày", fontsize=16)
        plt.xlabel("", fontsize=12)
        plt.ylabel("Số lượng giao dịch", fontsize=12)
        plt.grid(True)

        plt.xticks(rotation=45)
        plt.tight_layout()

        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        save_path = '/home/namdv/VSCode/DonationLookupBot/transaction_charts'
        filename = save_path + f"/chart_{timestamp}.png"

        plt.savefig(filename)
        dispatcher.utter_message(text = f"Biểu đồ mà bạn cần đã được lưu tại {filename}")
        