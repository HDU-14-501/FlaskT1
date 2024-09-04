from flask import Flask, jsonify, request, abort
from flask.views import MethodView
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from extention import db, cors
import models
from datetime import datetime, timedelta
from sqlalchemy import func
import random
from http import HTTPStatus
import dashscope
from dashscope import Generation

dashscope.api_key = "sk-68bc5e7308504a6caf8ace89d9a2ed5e"
app = Flask(__name__)


class Config(object):
    """配置参数"""
    user = 'FlaskVue'
    password = 'E7zBiJja7m2mTbkH'
    database = 'flaskvue'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@124.221.22.19:3306/%s' % (user, password, database)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
    app.config['JWT_SECRET_KEY'] = '12312131312'  # 设置 JWT 密钥


db.init_app(app)
cors.init_app(app, supports_credentials=True)
jwt = JWTManager(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.cli.command()
def create():
    db.drop_all()
    db.create_all()
    models.init_db_data()


# REST API 部分

# 登录视图类
class LoginAPI(MethodView):
    def post(self):
        data = request.get_json()
        print(data)
        if not data or not 'username' in data or not 'password' in data:
            abort(400, description="Missing Username or Password")

        username = data['username']
        password = data['password']

        # 在数据库中查找用户
        user = models.User.query.filter_by(Username=username).first()

        # 模拟错误，若用户名不存在或密码不正确
        if not user or user.Password != password:
            return jsonify({
                'code': 60204,
                'message': 'Account and password are incorrect.'
            }), 401

        # 用户验证成功，生成 JWT 令牌
        if user.Level == 1:
            access_token = 'admin-token'
        else:
            access_token = 'editor-token'

        return jsonify({
            'code': 20000,
            'data': {
                'token': access_token
            }
        }), 200


# 用户视图类
class UserAPI(MethodView):
    def get(self, uid=None):
        if uid:
            user = models.User.query.get(uid)
            if not user:
                abort(404)
            return jsonify({
                'UID': user.UID,
                'Username': user.Username,
                'Password': user.Password,
                'Name': user.Name,
                'RegisterTime': user.RegisterTime,
                'Level': user.Level
            })
        else:
            users = models.User.query.all()
            return jsonify([{
                'UID': user.UID,
                'Username': user.Username,
                'Password': user.Password,
                'Name': user.Name,
                'RegisterTime': user.RegisterTime,
                'Level': user.Level
            } for user in users])

    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ['Username', 'Password', 'Name', 'Level']):
            abort(400)

        new_user = models.User(
            Username=data['Username'],
            Password=data['Password'],
            Name=data['Name'],
            Level=data['Level']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201

    def put(self, uid):
        user = models.User.query.get(uid)
        if not user:
            abort(404)

        data = request.get_json()
        if 'Password' in data:
            user.Password = data['Password']
        if 'Name' in data:
            user.Name = data['Name']
        if 'Level' in data:
            user.Level = data['Level']

        db.session.commit()
        return jsonify({'message': 'User updated successfully'})

    def delete(self, uid):
        user = models.User.query.get(uid)
        if not user:
            abort(404)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})


# 家庭成员视图类
class FamilyMemberAPI(MethodView):
    def get(self, member_id=None):
        if member_id:
            member = models.FamilyMember.query.get(member_id)
            if not member:
                abort(404)
            return jsonify({
                'Id': member.Id,
                'Identity': member.Identity,
                'Membername': member.Membername
            })
        else:
            members = models.FamilyMember.query.all()
            return jsonify([{
                'Id': member.Id,
                'Identity': member.Identity,
                'Membername': member.Membername
            } for member in members])

    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ['Identity', 'Membername']):
            abort(400)

        new_member = models.FamilyMember(
            Identity=data['Identity'],
            Membername=data['Membername']
        )
        db.session.add(new_member)
        db.session.commit()
        return jsonify({'message': 'Family member created successfully'}), 201

    def put(self, member_id):
        member = models.FamilyMember.query.get(member_id)
        if not member:
            abort(404)

        data = request.get_json()
        if 'Identity' in data:
            member.Identity = data['Identity']
        if 'Membername' in data:
            member.Membername = data['Membername']

        db.session.commit()
        return jsonify({'message': 'Family member updated successfully'})

    def delete(self, member_id):
        member = models.FamilyMember.query.get(member_id)
        if not member:
            abort(404)
        db.session.delete(member)
        db.session.commit()
        return jsonify({'message': 'Family member deleted successfully'})


# 收入视图类
class IncomeAPI(MethodView):
    def get(self, income_id=None):
        if income_id:
            income = models.Income.query.get(income_id)
            if not income:
                abort(404)
            return jsonify({
                'ID': income.ID,
                'Time': income.Time,
                'Amount': income.Amount,
                'ClassifyID': income.ClassifyID,
                'Member': income.Member,
                'Place': income.Place,
                'Remark': income.Remark
            })
        else:
            incomes = models.Income.query.all()
            return jsonify([{
                'ID': income.ID,
                'Time': income.Time,
                'Amount': income.Amount,
                'ClassifyID': income.ClassifyID,
                'Member': income.Member,
                'Place': income.Place,
                'Remark': income.Remark
            } for income in incomes])

    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ['Time', 'Amount', 'ClassifyID', 'Member', 'Place', 'Remark']):
            abort(400)

        new_income = models.Income(
            Time=data['Time'],
            Amount=data['Amount'],
            ClassifyID=data['ClassifyID'],
            Member=data['Member'],
            Place=data['Place'],
            Remark=data['Remark']
        )
        db.session.add(new_income)
        db.session.commit()
        return jsonify({'message': 'Income created successfully'}), 201

    def put(self, income_id):
        income = models.Income.query.get(income_id)
        if not income:
            abort(404)

        data = request.get_json()
        if 'Amount' in data:
            income.Amount = data['Amount']
        if 'Place' in data:
            income.Place = data['Place']
        if 'Remark' in data:
            income.Remark = data['Remark']

        db.session.commit()
        return jsonify({'message': 'Income updated successfully'})

    def delete(self, income_id):
        income = models.Income.query.get(income_id)
        if not income:
            abort(404)
        db.session.delete(income)
        db.session.commit()
        return jsonify({'message': 'Income deleted successfully'})


# 支出视图类
class OutlayAPI(MethodView):
    def get(self, outlay_id=None):
        if outlay_id:
            outlay = models.Outlay.query.get(outlay_id)
            if not outlay:
                abort(404)
            return jsonify({
                'ID': outlay.ID,
                'Time': outlay.Time,
                'Amount': outlay.Amount,
                'ClassifyID': outlay.ClassifyID,
                'Member': outlay.Member,
                'Place': outlay.Place,
                'Remark': outlay.Remark
            })
        else:
            outlays = models.Outlay.query.all()
            return jsonify([{
                'ID': outlay.ID,
                'Time': outlay.Time,
                'Amount': outlay.Amount,
                'ClassifyID': outlay.ClassifyID,
                'Member': outlay.Member,
                'Place': outlay.Place,
                'Remark': outlay.Remark
            } for outlay in outlays])

    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ['Time', 'Amount', 'ClassifyID', 'Member', 'Place', 'Remark']):
            abort(400)

        new_outlay = models.Outlay(
            Time=data['Time'],
            Amount=data['Amount'],
            ClassifyID=data['ClassifyID'],
            Member=data['Member'],
            Place=data['Place'],
            Remark=data['Remark']
        )
        db.session.add(new_outlay)
        db.session.commit()
        return jsonify({'message': 'Outlay created successfully'}), 201

    def put(self, outlay_id):
        outlay = models.Outlay.query.get(outlay_id)
        if not outlay:
            abort(404)

        data = request.get_json()
        if 'Amount' in data:
            outlay.Amount = data['Amount']
        if 'Place' in data:
            outlay.Place = data['Place']
        if 'Remark' in data:
            outlay.Remark = data['Remark']

        db.session.commit()
        return jsonify({'message': 'Outlay updated successfully'})

    def delete(self, outlay_id):
        outlay = models.Outlay.query.get(outlay_id)
        if not outlay:
            abort(404)
        db.session.delete(outlay)
        db.session.commit()
        return jsonify({'message': 'Outlay deleted successfully'})


# 收入分类视图类
class IncomeClassifyAPI(MethodView):
    def get(self, classify_id=None):
        if classify_id:
            classify = models.IncomeClassify.query.get(classify_id)
            if not classify:
                abort(404)
            return jsonify({
                'ID': classify.ID,
                'Name': classify.Name,
                'FatherClassifyID': classify.FatherClassifyID
            })
        else:
            classifies = models.IncomeClassify.query.all()
            return jsonify([{
                'ID': classify.ID,
                'Name': classify.Name,
                'FatherClassifyID': classify.FatherClassifyID
            } for classify in classifies])

    def post(self):
        data = request.get_json()
        if not data or 'Name' not in data:
            abort(400)

        new_classify = models.IncomeClassify(
            Name=data['Name'],
            FatherClassifyID=data.get('FatherClassifyID')
        )
        db.session.add(new_classify)
        db.session.commit()
        return jsonify({'message': 'Income classify created successfully'}), 201

    def put(self, classify_id):
        classify = models.IncomeClassify.query.get(classify_id)
        if not classify:
            abort(404)

        data = request.get_json()
        if 'Name' in data:
            classify.Name = data['Name']
        if 'FatherClassifyID' in data:
            classify.FatherClassifyID = data['FatherClassifyID']

        db.session.commit()
        return jsonify({'message': 'Income classify updated successfully'})

    def delete(self, classify_id):
        classify = models.IncomeClassify.query.get(classify_id)
        if not classify:
            abort(404)
        db.session.delete(classify)
        db.session.commit()
        return jsonify({'message': 'Income classify deleted successfully'})


# 支出分类视图类
class OutlayClassifyAPI(MethodView):
    def get(self, classify_id=None):
        if classify_id:
            classify = models.OutlayClassify.query.get(classify_id)
            if not classify:
                abort(404)
            return jsonify({
                'ID': classify.ID,
                'Name': classify.Name,
                'FatherClassifyID': classify.FatherClassifyID
            })
        else:
            classifies = models.OutlayClassify.query.all()
            return jsonify([{
                'ID': classify.ID,
                'Name': classify.Name,
                'FatherClassifyID': classify.FatherClassifyID
            } for classify in classifies])

    def post(self):
        data = request.get_json()
        if not data or 'Name' not in data:
            abort(400)

        new_classify = models.OutlayClassify(
            Name=data['Name'],
            FatherClassifyID=data.get('FatherClassifyID')
        )
        db.session.add(new_classify)
        db.session.commit()
        return jsonify({'message': 'Outlay classify created successfully'}), 201

    def put(self, classify_id):
        classify = models.OutlayClassify.query.get(classify_id)
        if not classify:
            abort(404)

        data = request.get_json()
        if 'Name' in data:
            classify.Name = data['Name']
        if 'FatherClassifyID' in data:
            classify.FatherClassifyID = data['FatherClassifyID']

        db.session.commit()
        return jsonify({'message': 'Outlay classify updated successfully'})

    def delete(self, classify_id):
        classify = models.OutlayClassify.query.get(classify_id)
        if not classify:
            abort(404)
        db.session.delete(classify)
        db.session.commit()
        return jsonify({'message': 'Outlay classify deleted successfully'})


# 家庭成员统计视图类
class FamilyMemberCountAPI(MethodView):
    def get(self):
        # 统计家庭成员数量
        member_count = models.FamilyMember.query.count()
        return jsonify({
            'count': member_count - 1
        })


# 本月收入统计视图类
class MonthlyIncomeAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间和结束时间
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = datetime(now.year, now.month + 1, 1) - timedelta(seconds=1) if now.month < 12 else datetime(
            now.year, 12, 31, 23, 59, 59)

        # 查询本月收入总额
        total_income = db.session.query(db.func.sum(models.Income.Amount)).filter(
            models.Income.Time >= start_of_month,
            models.Income.Time <= end_of_month
        ).scalar()

        # 如果没有收入记录，返回0
        total_income = total_income or 0

        return jsonify({
            'total_income': total_income
        })


# 本月支出统计视图类
class MonthlyOutlayAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间和结束时间
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = datetime(now.year, now.month + 1, 1) - timedelta(seconds=1) if now.month < 12 else datetime(
            now.year, 12, 31, 23, 59, 59)

        # 查询本月支出总额
        total_outlay = db.session.query(db.func.sum(models.Outlay.Amount)).filter(
            models.Outlay.Time >= start_of_month,
            models.Outlay.Time <= end_of_month
        ).scalar()

        # 如果没有支出记录，返回0
        total_outlay = total_outlay or 0

        return jsonify({
            'total_outlay': total_outlay
        })


# 累计盈余统计视图类
class TotalSurplusAPI(MethodView):
    def get(self):
        # 查询总收入
        total_income = db.session.query(db.func.sum(models.Income.Amount)).scalar() or 0

        # 查询总支出
        total_outlay = db.session.query(db.func.sum(models.Outlay.Amount)).scalar() or 0

        # 计算盈余
        surplus = total_income - total_outlay

        return jsonify({
            'total_income': total_income,
            'total_outlay': total_outlay,
            'surplus': surplus
        })


class MonthlyTopOutlayCategoryAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间和结束时间
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)

        # 获取所有大类（没有父分类的分类）
        parent_categories = db.session.query(
            models.OutlayClassify.ID,
            models.OutlayClassify.Name
        ).filter(
            models.OutlayClassify.FatherClassifyID.is_(None)
        ).all()

        # 初始化变量以存储最大支出的大类和金额
        max_category = None
        max_total_outlay = 0

        for category in parent_categories:
            # 获取该大类及其所有子类ID
            subcategory_ids = db.session.query(models.OutlayClassify.ID).filter(
                models.OutlayClassify.FatherClassifyID == category.ID
            ).all()
            subcategory_ids = [id for (id,) in subcategory_ids]

            # 查询该大类及其所有子类的支出总额
            total_outlay = db.session.query(db.func.sum(models.Outlay.Amount)).filter(
                models.Outlay.Time >= start_of_month,
                models.Outlay.Time < end_of_month,
                models.Outlay.ClassifyID.in_(subcategory_ids + [category.ID])
            ).scalar() or 0

            # 检查是否是最大支出的大类
            if total_outlay > max_total_outlay:
                max_total_outlay = total_outlay
                max_category = category.Name

        # 返回最大支出的大类及其总额
        return jsonify({"TopCategory": max_category, "TotalOutlay": max_total_outlay})



from sqlalchemy import text


class IncomeOutlayEntryAPI(MethodView):
    def get(self):
        # 查询所有收入条目信息
        income_entries = db.session.query(
            models.Income.ID.label('ID'),
            models.Income.Time.label('Time'),
            models.Income.Amount.label('Amount'),
            models.IncomeClassify.Name.label('ClassifyName'),
            models.FamilyMember.Membername.label('Member'),
            models.Income.Place.label('Place'),
            models.Income.Remark.label('Remark'),  # 添加备注字段
            db.literal_column("'Income'").label('Type')  # 标记为收入
        ).join(models.IncomeClassify, models.Income.ClassifyID == models.IncomeClassify.ID) \
            .join(models.FamilyMember, models.Income.Member == models.FamilyMember.Id)

        # 查询所有支出条目信息
        outlay_entries = db.session.query(
            models.Outlay.ID.label('ID'),
            models.Outlay.Time.label('Time'),
            models.Outlay.Amount.label('Amount'),
            models.OutlayClassify.Name.label('ClassifyName'),
            models.FamilyMember.Membername.label('Member'),
            models.Outlay.Place.label('Place'),
            models.Outlay.Remark.label('Remark'),  # 添加备注字段
            db.literal_column("'Outlay'").label('Type')  # 标记为支出
        ).join(models.OutlayClassify, models.Outlay.ClassifyID == models.OutlayClassify.ID) \
            .join(models.FamilyMember, models.Outlay.Member == models.FamilyMember.Id)

        # 合并收入和支出的查询结果，并按时间排序
        entries = income_entries.union_all(outlay_entries).order_by(text('Time')).all()

        # 将查询结果转换为字典列表
        result = [
            {
                "ID": entry.ID,
                "Time": entry.Time.isoformat(),
                "Amount": entry.Amount,
                "ClassifyName": entry.ClassifyName,
                "Member": entry.Member,
                "Place": entry.Place,
                "Remark": entry.Remark,  # 添加备注字段到结果
                "Type": entry.Type
            }
            for entry in entries
        ]

        return jsonify(result)


class CreateIncomeOutlayEntryAPI(MethodView):
    def post(self):
        data = request.get_json()
        entry_type = data.get('Type')
        print(data)
        if entry_type == 'Income':
            new_entry = models.Income(
                Time=datetime.fromisoformat(data['Time']),
                Amount=data['Amount'],
                ClassifyID=data['ClassifyID'],
                Member=data['Member'],
                Place=data['Place'],
                Remark=data.get('Remark', '')
            )
            db.session.add(new_entry)

        elif entry_type == 'Outlay':
            new_entry = models.Outlay(
                Time=datetime.fromisoformat(data['Time']),
                Amount=data['Amount'],
                ClassifyID=data['ClassifyID'],
                Member=data['Member'],
                Place=data['Place'],
                Remark=data.get('Remark', '')
            )
            db.session.add(new_entry)

        else:
            abort(400, description="Invalid entry type")

        db.session.commit()
        return jsonify({'message': 'Record created successfully'}), 201


class UpdateDeleteIncomeOutlayEntryAPI(MethodView):
    def put(self, entry_id):
        data = request.get_json()
        entry_type = data.get('Type')
        print(data)
        if entry_type == '收入' or entry_type == 'Income':
            entry = models.Income.query.get(entry_id)
            if not entry:
                abort(404, description="Income record not found")

            if 'Time' in data:
                entry.Time = datetime.fromisoformat(data['Time'])
            if 'Amount' in data:
                entry.Amount = data['Amount']
            if 'ClassifyID' in data:
                entry.ClassifyID = data['ClassifyID']
            if 'Member' in data:
                entry.Member = data['Member']
            if 'Place' in data:
                entry.Place = data['Place']
            if 'Remark' in data:
                entry.Remark = data['Remark']

        elif entry_type == '支出' or entry_type == 'Outlay':
            entry = models.Outlay.query.get(entry_id)
            if not entry:
                abort(404, description="Outlay record not found")

            if 'Time' in data:
                entry.Time = datetime.fromisoformat(data['Time'])
            if 'Amount' in data:
                entry.Amount = data['Amount']
            if 'ClassifyID' in data:
                entry.ClassifyID = data['ClassifyID']
            if 'Member' in data:
                entry.Member = data['Member']
            if 'Place' in data:
                entry.Place = data['Place']
            if 'Remark' in data:
                entry.Remark = data['Remark']

        else:
            abort(400, description="Invalid entry type")

        db.session.commit()
        return jsonify({'message': 'Record updated successfully'}), 200

    def delete(self, entry_id):
        entry_type = request.args.get('Type')

        if entry_type == '收入' or entry_type == 'Income':
            entry = models.Income.query.get(entry_id)
            if not entry:
                abort(404, description="Income record not found")
            db.session.delete(entry)

        elif entry_type == '支出' or entry_type == 'Outlay':
            entry = models.Outlay.query.get(entry_id)
            if not entry:
                abort(404, description="Outlay record not found")
            db.session.delete(entry)

        else:
            abort(400, description="Invalid entry type")

        db.session.commit()
        return jsonify({'message': 'Record deleted successfully'}), 200


class FamilyTotalOutlayByCategoryAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间
        start_of_month = datetime(now.year, now.month, 1)

        # 查询所有父级支出分类（大类）
        parent_categories = db.session.query(
            models.OutlayClassify.ID,
            models.OutlayClassify.Name
        ).filter(models.OutlayClassify.FatherClassifyID.is_(None)).all()

        # 初始化返回数据
        result = []

        # 遍历所有大类，计算本月每个大类的总支出
        for category in parent_categories:
            total_outlay = db.session.query(db.func.sum(models.Outlay.Amount)).join(
                models.OutlayClassify,
                models.Outlay.ClassifyID == models.OutlayClassify.ID
            ).filter(
                models.OutlayClassify.FatherClassifyID == category.ID,
                models.Outlay.Time >= start_of_month,  # 过滤本月的记录
                models.Outlay.Time <= now  # 确保统计到当前时间
            ).scalar() or 0

            # 将结果添加到返回列表中
            result.append({
                "CategoryName": category.Name,
                "TotalOutlay": total_outlay
            })

        return jsonify(result)


class WeeklyOutlayByCategoryAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算七天前的日期
        seven_days_ago = now - timedelta(days=7)

        # 初始化返回的数据结构
        data = []

        # 查询每个家庭成员在近七天中的每天支出总额，排除“一家之主”
        members = db.session.query(models.FamilyMember).filter(models.FamilyMember.Membername != '一家之主').all()

        for member in members:
            member_data = {
                "name": member.Membername,
                "daily_outlays": []
            }
            for i in range(7):
                day = seven_days_ago + timedelta(days=i)
                next_day = day + timedelta(days=1)

                # 计算该成员在当天的支出总额
                total_outlay = db.session.query(db.func.sum(models.Outlay.Amount)).filter(
                    models.Outlay.Member == member.Id,
                    models.Outlay.Time >= day,
                    models.Outlay.Time < next_day
                ).scalar() or 0

                member_data["daily_outlays"].append({
                    "date": day.strftime('%Y-%m-%d'),
                    "total_outlay": total_outlay
                })

            # 将结果添加到数据中
            data.append(member_data)

        return jsonify(data)


class WeeklyIncomeAndOutlayByDayAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算七天前的日期
        seven_days_ago = now - timedelta(days=7)

        # 初始化返回的数据结构
        data = []

        # 按天统计收入和支出
        for i in range(7):
            day = seven_days_ago + timedelta(days=i)
            next_day = day + timedelta(days=1)

            # 计算当天的收入总额
            total_income = db.session.query(db.func.sum(models.Income.Amount)).filter(
                models.Income.Time >= day,
                models.Income.Time < next_day
            ).scalar() or 0

            # 计算当天的支出总额
            total_outlay = db.session.query(db.func.sum(models.Outlay.Amount)).filter(
                models.Outlay.Time >= day,
                models.Outlay.Time < next_day
            ).scalar() or 0

            # 将结果添加到数据中
            data.append({
                "date": day.strftime('%Y-%m-%d'),
                "total_income": total_income,
                "total_outlay": total_outlay
            })

        return jsonify(data)


class DailyOutlayByMemberAPI(MethodView):
    def get(self):
        # 获取所有独特的日期
        dates = db.session.query(func.date(models.Outlay.Time).label('date')).distinct().all()

        result = []

        for date_row in dates:
            date = date_row.date.isoformat()
            daily_data = {"Date": date, "Details": []}

            # 获取该日期下，每个家庭成员的支出总额
            members = db.session.query(
                models.FamilyMember.Membername,
                func.sum(models.Outlay.Amount).label('TotalOutlay')
            ).join(
                models.Outlay, models.Outlay.Member == models.FamilyMember.Id
            ).filter(
                func.date(models.Outlay.Time) == date
            ).group_by(models.FamilyMember.Membername).all()

            for member_name, total_outlay in members:
                daily_data["Details"].append({
                    "MemberName": member_name,
                    "TotalOutlay": total_outlay
                })

            result.append(daily_data)

        return jsonify(result)


class DailyIncomeAPI(MethodView):
    def get(self):
        # 查询每一天的收入总额
        daily_incomes = db.session.query(
            func.date(models.Income.Time).label('date'),
            func.sum(models.Income.Amount).label('total_income')
        ).group_by(
            func.date(models.Income.Time)
        ).order_by('date').all()

        # 初始化返回的数据结构
        result = []

        # 将查询结果格式化为指定的输出结构
        for income in daily_incomes:
            result.append({
                "Date": income.date.isoformat(),
                "TotalIncome": income.total_income
            })

        return jsonify(result)

class ChatAPI(MethodView):
    def post(self):
        data = request.get_json()
        print(data)
        if not data or not 'content' in data:
            abort(400, description="Missing content")

        user_input = data['content']

        messages = [{'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': user_input}]

        try:
            response = Generation.call(
                model="qwen-turbo",
                messages=messages,
                seed=random.randint(1, 10000),
                temperature=0.8,
                top_p=0.8,
                top_k=50,
                result_format='message'
            )

            if response.status_code == HTTPStatus.OK:
                return jsonify(response), HTTPStatus.OK
            else:
                return jsonify({
                    'code': response.status_code,
                    'message': response.message
                }), response.status_code
        except Exception as e:
            return jsonify({"code": 50000, "message": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

# 统计本月平均日支出
class MonthlyAverageDailyOutlayAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间和结束时间
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)

        # 查询本月总支出和天数
        total_outlay = db.session.query(db.func.sum(models.Outlay.Amount)).filter(
            models.Outlay.Time >= start_of_month,
            models.Outlay.Time < end_of_month
        ).scalar() or 0

        # 计算本月已经过去的天数
        days_past = (now - start_of_month).days + 1

        # 计算平均日支出
        avg_daily_outlay = total_outlay / days_past

        return jsonify({"AverageDailyOutlay": avg_daily_outlay})

# 统计本月总收入
class MonthlyTotalIncomeAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间和结束时间
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)

        # 查询本月收入总额
        total_income = db.session.query(db.func.sum(models.Income.Amount)).filter(
            models.Income.Time >= start_of_month,
            models.Income.Time < end_of_month
        ).scalar() or 0

        return jsonify({"TotalIncome": total_income})

# 统计本月总支出
class MonthlyTotalOutlayAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间和结束时间
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)

        # 查询本月支出总额
        total_outlay = db.session.query(db.func.sum(models.Outlay.Amount)).filter(
            models.Outlay.Time >= start_of_month,
            models.Outlay.Time < end_of_month
        ).scalar() or 0

        return jsonify({"TotalOutlay": total_outlay})

# 统计本月盈余
class MonthlySurplusAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间和结束时间
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)

        # 查询本月收入总额
        total_income = db.session.query(db.func.sum(models.Income.Amount)).filter(
            models.Income.Time >= start_of_month,
            models.Income.Time < end_of_month
        ).scalar() or 0

        # 查询本月支出总额
        total_outlay = db.session.query(db.func.sum(models.Outlay.Amount)).filter(
            models.Outlay.Time >= start_of_month,
            models.Outlay.Time < end_of_month
        ).scalar() or 0

        # 计算盈余
        surplus = total_income - total_outlay

        return jsonify({"Surplus": surplus})

# 今日支出最多的地点
class TodayTopOutlayLocationAPI(MethodView):
    def get(self):
        # 获取当前日期
        today = datetime.now().date()

        # 查询今日支出最多的地点
        top_location = db.session.query(
            models.Outlay.Place,
            db.func.sum(models.Outlay.Amount).label('total_outlay')
        ).filter(
            func.date(models.Outlay.Time) == today
        ).group_by(models.Outlay.Place).order_by(db.func.sum(models.Outlay.Amount).desc()).first()

        if top_location:
            return jsonify({"Place": top_location.Place, "TotalOutlay": top_location.total_outlay})
        else:
            return jsonify({"Place": None, "TotalOutlay": 0})


# 今日支出最多的分类
class TodayTopOutlayCategoryAPI(MethodView):
    def get(self):
        # 获取当前日期
        today = datetime.now().date()

        # 查询所有的大类
        parent_categories = db.session.query(
            models.OutlayClassify.ID,
            models.OutlayClassify.Name
        ).filter(models.OutlayClassify.FatherClassifyID.is_(None)).all()

        # 初始化一个变量来存储支出最多的大类和金额
        top_category = {"Category": None, "TotalOutlay": 0}

        # 遍历每个大类，计算其当天的总支出
        for category in parent_categories:
            # 获取该大类的所有子类ID
            subcategory_ids = db.session.query(models.OutlayClassify.ID).filter(
                models.OutlayClassify.FatherClassifyID == category.ID
            ).all()
            subcategory_ids = [id for (id,) in subcategory_ids]

            # 计算该大类当天的总支出，包括其所有子类的支出
            total_outlay = db.session.query(
                db.func.sum(models.Outlay.Amount)
            ).filter(
                models.Outlay.ClassifyID.in_(subcategory_ids),
                func.date(models.Outlay.Time) == today
            ).scalar() or 0

            # 更新支出最多的大类
            if total_outlay > top_category["TotalOutlay"]:
                top_category = {"Category": category.Name, "TotalOutlay": total_outlay}

        return jsonify(top_category)


# 本月支出最多的地点
class MonthlyTopOutlayLocationAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间和结束时间
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)

        # 查询本月支出最多的地点
        top_location = db.session.query(
            models.Outlay.Place,
            db.func.sum(models.Outlay.Amount).label('total_outlay')
        ).filter(
            models.Outlay.Time >= start_of_month,
            models.Outlay.Time < end_of_month
        ).group_by(models.Outlay.Place).order_by(db.func.sum(models.Outlay.Amount).desc()).first()

        if top_location:
            return jsonify({"Place": top_location.Place, "TotalOutlay": top_location.total_outlay})
        else:
            return jsonify({"Place": None, "TotalOutlay": 0})


class MonthlyOutlayByCategoryAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间
        start_of_month = datetime(now.year, now.month, 1)

        # 查询所有的父分类（大类）
        parent_categories = db.session.query(models.OutlayClassify).filter(
            models.OutlayClassify.FatherClassifyID.is_(None)).all()

        # 初始化返回的数据结构
        data = []

        # 查询每个家庭成员在每个大类中的支出总额，但排除“一家之主”
        members = db.session.query(models.FamilyMember).filter(models.FamilyMember.Membername != '一家之主').all()

        for member in members:
            member_data = {
                "name": member.Membername,
                "value": []
            }
            for category in parent_categories:
                # 计算该成员在该大类中的支出总额
                total_outlay = db.session.query(db.func.sum(models.Outlay.Amount)).join(
                    models.OutlayClassify,
                    models.Outlay.ClassifyID == models.OutlayClassify.ID
                ).filter(
                    models.Outlay.Member == member.Id,
                    models.Outlay.Time >= start_of_month,
                    models.OutlayClassify.FatherClassifyID == category.ID
                ).scalar() or 0
                member_data["value"].append(total_outlay)

            # 将结果添加到数据中
            data.append(member_data)

        return jsonify(data)
# 本月支出最多的分类
class MonthlyOutlayTopCategoryAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间和结束时间
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)

        # 获取所有大类（没有父分类的分类）
        parent_categories = db.session.query(
            models.OutlayClassify.ID,
            models.OutlayClassify.Name
        ).filter(
            models.OutlayClassify.FatherClassifyID.is_(None)
        ).all()

        # 初始化变量以存储最大支出的大类和金额
        max_category = None
        max_total_outlay = 0

        for category in parent_categories:
            # 获取该大类及其所有子类ID
            subcategory_ids = db.session.query(models.OutlayClassify.ID).filter(
                models.OutlayClassify.FatherClassifyID == category.ID
            ).all()
            subcategory_ids = [id for (id,) in subcategory_ids]

            # 查询该大类及其所有子类的支出总额
            total_outlay = db.session.query(db.func.sum(models.Outlay.Amount)).filter(
                models.Outlay.Time >= start_of_month,
                models.Outlay.Time < end_of_month,
                models.Outlay.ClassifyID.in_(subcategory_ids + [category.ID])
            ).scalar() or 0

            # 检查是否是最大支出的大类
            if total_outlay > max_total_outlay:
                max_total_outlay = total_outlay
                max_category = category.Name

        # 返回最大支出的大类及其总额
        return jsonify({"TopCategory": max_category, "TotalOutlay": max_total_outlay})




# 统计今日支出
class TodayTotalOutlayAPI(MethodView):
    def get(self):
        # 获取当前日期
        today = datetime.now().date()

        # 计算今日的总支出
        total_outlay = db.session.query(
            db.func.sum(models.Outlay.Amount)
        ).filter(
            func.date(models.Outlay.Time) == today
        ).scalar() or 0

        return jsonify({"TotalOutlay": total_outlay})

# 注册 API 路由
app.add_url_rule('/api/today_total_outlay', view_func=TodayTotalOutlayAPI.as_view('today_total_outlay_api'))

# 统计今日收入
class TodayTotalIncomeAPI(MethodView):
    def get(self):
        # 获取当前日期
        today = datetime.now().date()

        # 计算今日的总收入
        total_income = db.session.query(
            db.func.sum(models.Income.Amount)
        ).filter(
            func.date(models.Income.Time) == today
        ).scalar() or 0

        return jsonify({"TotalIncome": total_income})


class RealEstateAPI(MethodView):
    def get(self, real_estate_id=None):
        if real_estate_id:
            real_estate = models.RealEstate.query.get(real_estate_id)
            if not real_estate:
                abort(404, description="Real estate not found")
            return jsonify({
                'ID': real_estate.ID,
                'Title': real_estate.Title,  # 添加 Title 字段
                'Address': real_estate.Address,
                'Owner': real_estate.Owner,
                'PurchaseDate': real_estate.PurchaseDate.isoformat(),
                'PurchaseAmount': real_estate.PurchaseAmount,
                'BasicInfo': real_estate.BasicInfo,
                'Rent': real_estate.Rent,
                'Tenant': real_estate.Tenant,
                'LeaseEndDate': real_estate.LeaseEndDate.isoformat() if real_estate.LeaseEndDate else None,
                'RentDueDay': real_estate.RentDueDay,
                'IsAvailableForRent': real_estate.IsAvailableForRent,
                'ImageURL': real_estate.ImageURL
            })
        else:
            real_estates = models.RealEstate.query.all()
            return jsonify([{
                'ID': real_estate.ID,
                'Title': real_estate.Title,  # 添加 Title 字段
                'Address': real_estate.Address,
                'Owner': real_estate.Owner,
                'PurchaseDate': real_estate.PurchaseDate.isoformat(),
                'PurchaseAmount': real_estate.PurchaseAmount,
                'BasicInfo': real_estate.BasicInfo,
                'Rent': real_estate.Rent,
                'Tenant': real_estate.Tenant,
                'LeaseEndDate': real_estate.LeaseEndDate.isoformat() if real_estate.LeaseEndDate else None,
                'RentDueDay': real_estate.RentDueDay,
                'IsAvailableForRent': real_estate.IsAvailableForRent,
                'ImageURL': real_estate.ImageURL
            } for real_estate in real_estates])

    def post(self):
        data = request.get_json()
        if not data or not all(key in data for key in ['Address', 'Owner', 'PurchaseDate', 'PurchaseAmount', 'Title']):
            abort(400, description="Missing required fields")

        new_real_estate = models.RealEstate(
            Title=data['Title'],  # 添加 Title 字段
            Address=data['Address'],
            Owner=data['Owner'],
            PurchaseDate=datetime.fromisoformat(data['PurchaseDate']),
            PurchaseAmount=data['PurchaseAmount'],
            BasicInfo=data.get('BasicInfo'),
            Rent=data.get('Rent'),
            Tenant=data.get('Tenant'),
            LeaseEndDate=datetime.fromisoformat(data['LeaseEndDate']) if 'LeaseEndDate' in data else None,
            RentDueDay=data.get('RentDueDay'),
            IsAvailableForRent=data.get('IsAvailableForRent', True),
            ImageURL=data.get('ImageURL')
        )
        db.session.add(new_real_estate)
        db.session.commit()
        return jsonify({'message': 'Real estate created successfully'}), 201

    def put(self, real_estate_id):
        real_estate = models.RealEstate.query.get(real_estate_id)
        if not real_estate:
            abort(404, description="Real estate not found")

        data = request.get_json()
        if 'Title' in data:  # 更新 Title 字段
            real_estate.Title = data['Title']
        if 'Address' in data:
            real_estate.Address = data['Address']
        if 'Owner' in data:
            real_estate.Owner = data['Owner']
        if 'PurchaseDate' in data:
            real_estate.PurchaseDate = datetime.fromisoformat(data['PurchaseDate'])
        if 'PurchaseAmount' in data:
            real_estate.PurchaseAmount = data['PurchaseAmount']
        if 'BasicInfo' in data:
            real_estate.BasicInfo = data['BasicInfo']
        if 'Rent' in data:
            real_estate.Rent = data['Rent']
        if 'Tenant' in data:
            real_estate.Tenant = data['Tenant']
        if 'LeaseEndDate' in data:
            real_estate.LeaseEndDate = datetime.fromisoformat(data['LeaseEndDate'])
        if 'RentDueDay' in data:
            real_estate.RentDueDay = data['RentDueDay']
        if 'IsAvailableForRent' in data:
            real_estate.IsAvailableForRent = data['IsAvailableForRent']
        if 'ImageURL' in data:
            real_estate.ImageURL = data['ImageURL']

        db.session.commit()
        return jsonify({'message': 'Real estate updated successfully'})

    def delete(self, real_estate_id):
        real_estate = models.RealEstate.query.get(real_estate_id)
        if not real_estate:
            abort(404, description="Real estate not found")
        db.session.delete(real_estate)
        db.session.commit()
        return jsonify({'message': 'Real estate deleted successfully'})


# 注册 RealEstate API 路由
real_estate_view = RealEstateAPI.as_view('real_estate_api')
app.add_url_rule('/api/real_estates/', defaults={'real_estate_id': None}, view_func=real_estate_view, methods=['GET'])
app.add_url_rule('/api/real_estates/<int:real_estate_id>', view_func=real_estate_view, methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/api/real_estates/', view_func=real_estate_view, methods=['POST'])


# 注册 API 路由
app.add_url_rule('/api/today_total_income', view_func=TodayTotalIncomeAPI.as_view('today_total_income_api'))

# 添加API路由
app.add_url_rule('/api/today_top_outlay_location', view_func=TodayTopOutlayLocationAPI.as_view('today_top_outlay_location_api'))
app.add_url_rule('/api/today_top_outlay_category', view_func=TodayTopOutlayCategoryAPI.as_view('today_top_outlay_category_api'))
app.add_url_rule('/api/monthly_top_outlay_location', view_func=MonthlyTopOutlayLocationAPI.as_view('monthly_top_outlay_location_api'))
app.add_url_rule('/api/monthly_top_outlay_item', view_func=MonthlyOutlayTopCategoryAPI.as_view('monthly_top_outlay_item_api'))


# 添加API路由
app.add_url_rule('/api/monthly_average_daily_outlay', view_func=MonthlyAverageDailyOutlayAPI.as_view('monthly_average_daily_outlay_api'))
app.add_url_rule('/api/monthly_total_income', view_func=MonthlyTotalIncomeAPI.as_view('monthly_total_income_api'))
app.add_url_rule('/api/monthly_total_outlay', view_func=MonthlyTotalOutlayAPI.as_view('monthly_total_outlay_api'))
app.add_url_rule('/api/monthly_surplus', view_func=MonthlySurplusAPI.as_view('monthly_surplus_api'))


app.add_url_rule('/api/daily_income', view_func=DailyIncomeAPI.as_view('daily_income_api'))

# 将API路由添加到Flask应用程序中
app.add_url_rule('/api/daily_outlay_by_member', view_func=DailyOutlayByMemberAPI.as_view('daily_outlay_by_member_api'))

# 注册 API 路由
app.add_url_rule('/api/weekly_income_outlay',
                 view_func=WeeklyIncomeAndOutlayByDayAPI.as_view('weekly_income_outlay_api'), methods=['GET'])

# 注册 API 路由
app.add_url_rule('/api/weekly_outlay_by_category',
                 view_func=WeeklyOutlayByCategoryAPI.as_view('weekly_outlay_by_category_api'), methods=['GET'])

# 注册 API 路由
app.add_url_rule('/api/family_total_outlay_by_category',
                 view_func=FamilyTotalOutlayByCategoryAPI.as_view('family_total_outlay_by_category_api'),
                 methods=['GET'])

# 注册 API 路由
app.add_url_rule('/api/income_outlay_entries', view_func=IncomeOutlayEntryAPI.as_view('income_outlay_entry_api'),
                 methods=['GET'])
app.add_url_rule('/api/income_outlay_entries',
                 view_func=CreateIncomeOutlayEntryAPI.as_view('create_income_outlay_entry_api'), methods=['POST'])
app.add_url_rule('/api/income_outlay_entries/<int:entry_id>',
                 view_func=UpdateDeleteIncomeOutlayEntryAPI.as_view('update_delete_income_outlay_entry_api'),
                 methods=['PUT', 'DELETE'])

# 注册 API 路由
monthly_outlay_by_category_view = MonthlyOutlayByCategoryAPI.as_view('monthly_outlay_by_category_api')
app.add_url_rule('/api/outlay/total/by_category', view_func=monthly_outlay_by_category_view, methods=['GET'])

# 注册 API 路由
total_surplus_view = TotalSurplusAPI.as_view('total_surplus_api')
app.add_url_rule('/api/surplus/total', view_func=total_surplus_view, methods=['GET'])

# 注册 API 路由
monthly_outlay_view = MonthlyOutlayAPI.as_view('monthly_outlay_api')
app.add_url_rule('/api/outlay/total/month', view_func=monthly_outlay_view, methods=['GET'])

# 注册 API 路由
monthly_income_view = MonthlyIncomeAPI.as_view('monthly_income_api')
app.add_url_rule('/api/income/total/month', view_func=monthly_income_view, methods=['GET'])

# 注册 API 路由
family_member_count_view = FamilyMemberCountAPI.as_view('family_member_count_api')
app.add_url_rule('/api/family_members/count', view_func=family_member_count_view, methods=['GET'])

# 注册 API 路由
login_view = LoginAPI.as_view('login_api')
app.add_url_rule('/api/login', view_func=login_view, methods=['POST'])

user_view = UserAPI.as_view('user_api')
app.add_url_rule('/api/users/', defaults={'uid': None}, view_func=user_view, methods=['GET'])
app.add_url_rule('/api/users/<int:uid>', view_func=user_view, methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/api/users/', view_func=user_view, methods=['POST'])

family_member_view = FamilyMemberAPI.as_view('family_member_api')
app.add_url_rule('/api/family_members/', defaults={'member_id': None}, view_func=family_member_view, methods=['GET'])
app.add_url_rule('/api/family_members/<int:member_id>', view_func=family_member_view, methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/api/family_members/', view_func=family_member_view, methods=['POST'])

income_view = IncomeAPI.as_view('income_api')
app.add_url_rule('/api/incomes/', defaults={'income_id': None}, view_func=income_view, methods=['GET'])
app.add_url_rule('/api/incomes/<int:income_id>', view_func=income_view, methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/api/incomes/', view_func=income_view, methods=['POST'])

outlay_view = OutlayAPI.as_view('outlay_api')
app.add_url_rule('/api/outlays/', defaults={'outlay_id': None}, view_func=outlay_view, methods=['GET'])
app.add_url_rule('/api/outlays/<int:outlay_id>', view_func=outlay_view, methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/api/outlays/', view_func=outlay_view, methods=['POST'])

income_classify_view = IncomeClassifyAPI.as_view('income_classify_api')
app.add_url_rule('/api/income_classifies/', defaults={'classify_id': None}, view_func=income_classify_view,
                 methods=['GET'])
app.add_url_rule('/api/income_classifies/<int:classify_id>', view_func=income_classify_view,
                 methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/api/income_classifies/', view_func=income_classify_view, methods=['POST'])

outlay_classify_view = OutlayClassifyAPI.as_view('outlay_classify_api')
app.add_url_rule('/api/outlay_classifies/', defaults={'classify_id': None}, view_func=outlay_classify_view,
                 methods=['GET'])
app.add_url_rule('/api/outlay_classifies/<int:classify_id>', view_func=outlay_classify_view,
                 methods=['GET', 'PUT', 'DELETE'])
app.add_url_rule('/api/outlay_classifies/', view_func=outlay_classify_view, methods=['POST'])

chat_view = ChatAPI.as_view('chat_api')
app.add_url_rule('/api/chat', view_func=chat_view, methods=['POST'])

if __name__ == '__main__':
    app.run()
