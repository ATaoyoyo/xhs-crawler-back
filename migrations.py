import uuid
from flask_migrate import Migrate

migrate = Migrate()

from app import db
from app.api.models.admin_user import AdminUserModel
from werkzeug.security import generate_password_hash


def create_admin_table():
    """创建管理员表"""
    from app import create_app
    app = create_app('development')
    with app.app_context():
        db.create_all()
        print("admin_user 表创建成功")


def seed_admin_user():
    """添加默认管理员种子数据"""
    from app import create_app
    app = create_app('development')
    with app.app_context():
        existing = AdminUserModel.find_by_username('admin')
        if existing:
            print("管理员 admin 已存在，跳过")
            return

        salt = uuid.uuid4().hex
        password = generate_password_hash('{}{}'.format(salt, 'admin123'))

        admin = AdminUserModel(
            username='admin',
            password=password,
            salt=salt,
            role='admin',
            is_active=True
        )
        admin.add()
        print("默认管理员创建成功: admin/admin123")


def run_migration():
    """执行数据库迁移"""
    create_admin_table()
    seed_admin_user()


if __name__ == '__main__':
    run_migration()