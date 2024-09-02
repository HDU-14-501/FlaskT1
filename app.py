from flask import Flask, jsonify, request, abort
from flask.views import MethodView
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from extention import db, cors
import models
from datetime import datetime, timedelta
from sqlalchemy import func
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
                'Name': user.Name,
                'RegisterTime': user.RegisterTime,
                'Level': user.Level
            })
        else:
            users = models.User.query.all()
            return jsonify([{
                'UID': user.UID,
                'Username': user.Username,
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


class MonthlyOutlayByCategoryAPI(MethodView):
    def get(self):
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间
        start_of_month = datetime(now.year, now.month, 1)

        # 查询所有的父分类（大类）
        parent_categories = db.session.query(models.OutlayClassify).filter(models.OutlayClassify.FatherClassifyID.is_(None)).all()

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



# 注册 API 路由
app.add_url_rule('/api/weekly_income_outlay', view_func=WeeklyIncomeAndOutlayByDayAPI.as_view('weekly_income_outlay_api'), methods=['GET'])



# 注册 API 路由
app.add_url_rule('/api/weekly_outlay_by_category', view_func=WeeklyOutlayByCategoryAPI.as_view('weekly_outlay_by_category_api'), methods=['GET'])


# 注册 API 路由
app.add_url_rule('/api/family_total_outlay_by_category', view_func=FamilyTotalOutlayByCategoryAPI.as_view('family_total_outlay_by_category_api'), methods=['GET'])


# 注册 API 路由
app.add_url_rule('/api/income_outlay_entries', view_func=IncomeOutlayEntryAPI.as_view('income_outlay_entry_api'), methods=['GET'])
app.add_url_rule('/api/income_outlay_entries', view_func=CreateIncomeOutlayEntryAPI.as_view('create_income_outlay_entry_api'), methods=['POST'])
app.add_url_rule('/api/income_outlay_entries/<int:entry_id>', view_func=UpdateDeleteIncomeOutlayEntryAPI.as_view('update_delete_income_outlay_entry_api'), methods=['PUT', 'DELETE'])




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

if __name__ == '__main__':
    app.run()
