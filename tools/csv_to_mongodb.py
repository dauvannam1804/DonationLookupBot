from pymongo import MongoClient
import pandas as pd

# # Kết nối tới MongoDB cục bộ
# client = MongoClient("mongodb://localhost:27017/")

# # Kết nối với database và collection
# db = client['your_database_name']
# collection = db['your_collection_name']

# Đọc file CSV bằng pandas
df = pd.read_csv('data/transactions.csv')
print(df.head())
# Chuyển đổi DataFrame thành danh sách từ điển
data = df.to_dict(orient='records')
print(type(data))
print(data[0])

# # Thêm dữ liệu vào MongoDB
# collection.insert_many(data)

# print("Dữ liệu đã được thêm thành công vào MongoDB!")