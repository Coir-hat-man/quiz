# quiz
an online platform to help students do exercises.

运行此项目分为如下几个步骤

收集静态文件
python manage.py collectstatic
迁移数据库
python manage.py makemigrations
python manage.py migrate
注意，如果需要将数据库切换为MySQL，请在 settings.py文件里面注释掉sqlite的配置，添加MySQL的配置

DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': BASE_DIR / 'db.sqlite3',
     }
}

# 连接MySQL数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wxapp',     # 需要连接的数据库名称
        'USER': 'root',      # 数据库的用户名
        'PASSWORD': 'zhao',  # 连接密码
        'HOST': '127.0.0.1', # 主机
        'PORT': '3306',      # 端口
        'OPTIONS': {
            'charset': 'utf8mb4',  # 设置编码格式
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
启动项目
python manage.py runserver
也可以指定启动的端口（默认8000）

python manage.py runserver 0.0.0.0:80
