import requests

# POST 请求：插入数据
post_data = {
    "Address": "789 Birch Street, Springfield",
    "Owner": "张四",
    "PurchaseDate": "2023-01-01",
    "PurchaseAmount": 2500000.00,
    "BasicInfo": "五室两厅，面积200平米，带地下室",
    "Rent": 7000.00,
    "Tenant": "赵五",
    "LeaseEndDate": "2025-12-31",
    "RentDueDay": 10,
    "IsAvailableForRent": True,
    "ImageURL": "https://example.com/image.png"
}
response = requests.post('http://127.0.0.1:5000/api/real_estates/', json=post_data)
print(response.json())

# PUT 请求：更新数据
put_data = {
    "Rent": 7500.00,
    "Tenant": "王八",
    "IsAvailableForRent": False
}
response = requests.put('http://127.0.0.1:5000/api/real_estates/60002', json=put_data)
print(response.json())

# DELETE 请求：删除数据
response = requests.delete('http://127.0.0.1:5000/api/real_estates/60002')
print(response.json())
