from datetime import datetime
from sqlalchemy import func
from models import Outlay
from extention import db, cors

def calculate_monthly_expense(year, month):
    """
    计算特定月份的支出总金额。

    :param year: 年份，例如 2023
    :param month: 月份，1 到 12
    :return: 特定月份的支出总金额
    """
    # 构造该月份的第一天和下个月的第一天
    start_date = datetime(year, month, 1)
    if month == 12:  # 如果是12月，下一年1月1日
        end_date = datetime(year + 1, 1, 1)
    else:  # 否则，下个月的第一天
        end_date = datetime(year, month + 1, 1)

    # 查询该月份的支出总金额
    total_expense = db.session.query(func.sum(Outlay.Amount)).filter(
        Outlay.Time >= start_date,
        Outlay.Time < end_date
    ).scalar()

    return total_expense


def calculate_annual_expense(year):
    """
    计算特定年份的支出总金额。

    :param year: 年份，例如 2023
    :return: 特定年份的支出总金额
    """
    # 构造该年份的第一天和下一年的第一天
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)

    # 查询该年份的支出总金额
    total_expense = db.session.query(func.sum(Outlay.Amount)).filter(
        Outlay.Time >= start_date,
        Outlay.Time < end_date
    ).scalar()

    return total_expense