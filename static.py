from models import Outlay

# 特定类型支出总金额
def calculate_total_expense_by_type(outlay_type):
    outlays = Outlay.query.filter(Outlay.ClassifyID == outlay_type).all()
    total_expense = 0
    for outlay in outlays:
        total_expense += outlay.Amount

    return total_expense

# 统计餐饮支出主要是在哪些商家消费的，这里返回的是所有商家的消费数据
def get_all_shop_expense():
    outlays = Outlay.query.all()
    place_expense = {}
    for outlay in outlays:
        if place_expense.get(outlay.Place):
            place_expense[outlay.Place] += outlay.Amout
        else:
            place_expense[outlay.Place] = outlay.Amout
    return place_expense

# 统计所有消费过的餐厅的空间分布，这里返回的是所有地点的消费数据
def get_all_region_expense():
    outlays = Outlay.query.all()
    place_expense = {}
    for outlay in outlays:
        if place_expense.get(outlay.Region):
            place_expense[outlay.Region] += outlay.Amout
        else:
            place_expense[outlay.Region] = outlay.Amout
    return place_expense

