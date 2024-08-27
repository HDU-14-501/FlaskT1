from flask import Flask, jsonify, request, abort
from flask.views import MethodView
from flask_cors import CORS
from extention import db, cors
import models

app = Flask(__name__)


class Config(object):
    """配置参数"""
    # 设置连接数据库的URL
    user = 'FlaskVue'
    password = 'E7zBiJja7m2mTbkH'
    database = 'flaskvue'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@124.221.22.19:3306/%s' % (user, password, database)

    # 设置sqlalchemy自动更跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 查询时会显示原始SQL语句
    app.config['SQLALCHEMY_ECHO'] = True

    # 禁止自动提交数据处理
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False


db.init_app(app)
cors.init_app(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.cli.command()
def create():
    db.drop_all()
    db.create_all()
    models.init_db_data()


# REST API 部分

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



# 注册 API 路由
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
