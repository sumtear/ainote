import os

# 数据库配置
DB_CONFIG = {
    'username': os.environ.get('DB_USERNAME', 'root'),
    'password': os.environ.get('DB_PASSWORD', '253838'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'ai_notebook')
}

def get_db_uri():
    """获取数据库URI"""
    return f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"