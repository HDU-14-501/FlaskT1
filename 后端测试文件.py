import requests

# 1. POST 请求：插入数据
def test_post_real_estate():
    post_data = {
        "Title": "Springfield Grand Villa",  # 添加标题字段
        "Address": "789 Birch Street, Springfield",
        "Owner": "张四",
        "PurchaseDate": "2023-01-01",
        "PurchaseAmount": 2500000.00,
        "BasicInfo": "五室两厅，面积200平米，带地下室",
        "Rent": 7000.00,
        "Tenant": "赵五",
        "LeaseEndDate": "2025-12-31",
        "RentDueDay": 10,
        "IsAvailableForRent": 1,
        "ImageURL": "https://example.com/image.png"
    }
    response = requests.post('http://127.0.0.1:5000/api/real_estates/', json=post_data)
    print("POST Response:", response.json())

# 2. PUT 请求：更新数据
def test_put_real_estate():
    put_data = {
        "Rent": 7500.00,
        "Tenant": "王八",
        "IsAvailableForRent": 0
    }
    response = requests.put('http://127.0.0.1:5000/api/real_estates/60002', json=put_data)
    print("PUT Response:", response.json())

# 3. DELETE 请求：删除数据
def test_delete_real_estate():
    response = requests.delete('http://127.0.0.1:5000/api/real_estates/60002')
    print("DELETE Response:", response.json())

# 执行测试
if __name__ == "__main__":
    test_post_real_estate()  # 插入新数据
    test_put_real_estate()   # 更新数据
    test_delete_real_estate()  # 删除数据
