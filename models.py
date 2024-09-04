from datetime import datetime
from extention import db


# 用户表
class User(db.Model):
    __tablename__ = 'user'

    UID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Name = db.Column(db.String(50), nullable=False)
    RegisterTime = db.Column(db.DateTime, default=datetime.utcnow)
    Level = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<User {self.Username}>'


# 家庭成员表
class FamilyMember(db.Model):
    __tablename__ = 'family_member'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Identity = db.Column(db.String(50), nullable=False)  # 身份（如家长、子女等）
    Membername = db.Column(db.String(50), nullable=False)  # 成员名字

    def __repr__(self):
        return f'<FamilyMember {self.Membername}>'


# 收入分类表
class IncomeClassify(db.Model):
    __tablename__ = 'income_classify'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(50), nullable=False)
    FatherClassifyID = db.Column(db.Integer, db.ForeignKey('income_classify.ID'))  # 自关联，父分类

    father_classify = db.relationship('IncomeClassify', remote_side=[ID], backref='subclassifications')

    def __repr__(self):
        return f'<IncomeClassify {self.Name}>'


# 支出分类表
class OutlayClassify(db.Model):
    __tablename__ = 'outlay_classify'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(50), nullable=False)
    FatherClassifyID = db.Column(db.Integer, db.ForeignKey('outlay_classify.ID'))  # 自关联，父分类

    father_classify = db.relationship('OutlayClassify', remote_side=[ID], backref='subclassifications')

    def __repr__(self):
        return f'<OutlayClassify {self.Name}>'


# 收入表
class Income(db.Model):
    __tablename__ = 'income'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    Amount = db.Column(db.Float, nullable=False)
    ClassifyID = db.Column(db.Integer, db.ForeignKey('income_classify.ID'), nullable=False)  # 收入分类
    Member = db.Column(db.Integer, db.ForeignKey('family_member.Id'), nullable=False)  # 家庭成员
    Place = db.Column(db.String(255), nullable=True)
    Remark = db.Column(db.String(255), nullable=True)

    classify = db.relationship('IncomeClassify', backref='incomes')
    family_member = db.relationship('FamilyMember', backref='incomes')

    def __repr__(self):
        return f'<Income {self.Amount} from {self.Place}>'


# 支出表
class Outlay(db.Model):
    __tablename__ = 'outlay'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    Amount = db.Column(db.Float, nullable=False)
    ClassifyID = db.Column(db.Integer, db.ForeignKey('outlay_classify.ID'), nullable=False)  # 支出分类
    Member = db.Column(db.Integer, db.ForeignKey('family_member.Id'), nullable=False)  # 家庭成员
    Place = db.Column(db.String(255), nullable=True)
    Remark = db.Column(db.String(255), nullable=True)

    classify = db.relationship('OutlayClassify', backref='outlays')
    family_member = db.relationship('FamilyMember', backref='outlays')

    def __repr__(self):
        return f'<Outlay {self.Amount} at {self.Place}>'


# 初始化数据
def init_db_data():
    # 添加用户数据
    users = [
        User(UID=10001, Username='admin', Password='123456', Name='管理员', RegisterTime=datetime(2024, 8, 26, 12, 0),
             Level=1),
        User(UID=10002, Username='child1', Password='123456', Name='子女1', RegisterTime=datetime(2024, 8, 26, 12, 0),
             Level=1)
    ]

    # 添加家庭成员数据
    family_members = [
        FamilyMember(Id=20001, Identity='家长', Membername='王明'),
        FamilyMember(Id=20002, Identity='家长', Membername='李红'),
        FamilyMember(Id=20003, Identity='子女', Membername='王刚'),
        FamilyMember(Id=20004, Identity='子女', Membername='王勇')
    ]

    # 添加收入分类数据
    income_classifies = [
        IncomeClassify(ID=50001, Name='工资', FatherClassifyID=None),
        IncomeClassify(ID=50002, Name='基础工资', FatherClassifyID=50001),
        IncomeClassify(ID=50003, Name='奖金', FatherClassifyID=50001)
    ]

    # 添加支出分类数据
    outlay_classifies = [
        OutlayClassify(ID=60001, Name='购物支出', FatherClassifyID=None),
        OutlayClassify(ID=60002, Name='日用品', FatherClassifyID=60001)
    ]

    # 添加收入数据
    incomes = [
        Income(ID=30002, Time=datetime(2024, 9, 26, 12, 0), Amount=1000, ClassifyID=50001, Member=20001,
               Place='杭州电子科技大学', Remark='无')
    ]

    # 添加支出数据
    outlays = [
        Outlay(ID=40001, Time=datetime(2024, 8, 26, 12, 0), Amount=1000, ClassifyID=60001, Member=20001,
               Place='杭州电子科技大学', Remark='无')
    ]

    # 将所有数据添加到会话中
    db.session.add_all(users + family_members + income_classifies + outlay_classifies + incomes + outlays)

    # 提交数据
    db.session.commit()
    print("数据库已初始化测试数据")


class RealEstate(db.Model):
    __tablename__ = 'RealEstate'  # 指定表名
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Address = db.Column(db.String(255), nullable=False, comment='房屋所在地址')
    Owner = db.Column(db.String(100), nullable=False, comment='房屋所有人')
    PurchaseDate = db.Column(db.Date, nullable=False, comment='购入时间')
    PurchaseAmount = db.Column(db.Numeric(15, 2), nullable=False, comment='购入金额')
    BasicInfo = db.Column(db.Text, comment='房屋基本信息')
    Rent = db.Column(db.Numeric(10, 2), comment='租金')
    Tenant = db.Column(db.String(100), comment='租户')
    LeaseEndDate = db.Column(db.Date, comment='租期截止日期')
    RentDueDay = db.Column(db.Integer, comment='交租日期（每月第几日）')
    IsAvailableForRent = db.Column(db.Boolean, comment='可否租用')
    ImageURL = db.Column(db.String(255), comment='房屋图片URL')

