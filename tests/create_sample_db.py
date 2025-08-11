"""
SQLite3桌面工具使用示例
这个脚本会创建一个示例数据库用于测试工具功能
"""

import sqlite3
import os


def create_sample_database():
    """创建一个示例数据库"""
    db_path = "sample.db"

    # 如果文件已存在，删除它
    if os.path.exists(db_path):
        os.remove(db_path)

    # 创建数据库连接
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建用户表
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 创建产品表
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT,
            in_stock BOOLEAN DEFAULT 1
        )
    """)

    # 创建订单表
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)

    # 插入示例用户数据
    users_data = [
        ("张三", "zhangsan@example.com", 25),
        ("李四", "lisi@example.com", 30),
        ("王五", "wangwu@example.com", 28),
        ("赵六", "zhaoliu@example.com", 35),
        ("孙七", "sunqi@example.com", 22),
    ]

    cursor.executemany(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", users_data
    )

    # 插入示例产品数据
    products_data = [
        ("笔记本电脑", 5999.00, "电子产品", 1),
        ("无线鼠标", 99.00, "电子产品", 1),
        ("键盘", 299.00, "电子产品", 1),
        ("显示器", 1299.00, "电子产品", 1),
        ("办公椅", 899.00, "办公用品", 1),
        ("书桌", 1599.00, "办公用品", 1),
    ]

    cursor.executemany(
        "INSERT INTO products (name, price, category, in_stock) VALUES (?, ?, ?, ?)",
        products_data,
    )

    # 插入示例订单数据
    orders_data = [
        (1, 1, 1),  # 张三买了1台笔记本电脑
        (2, 2, 2),  # 李四买了2个无线鼠标
        (3, 3, 1),  # 王五买了1个键盘
        (1, 4, 1),  # 张三买了1个显示器
        (4, 5, 1),  # 赵六买了1个办公椅
    ]

    cursor.executemany(
        "INSERT INTO orders (user_id, product_id, quantity) VALUES (?, ?, ?)",
        orders_data,
    )

    # 提交更改并关闭连接
    conn.commit()
    conn.close()

    print(f"示例数据库 '{db_path}' 创建成功！")
    print("包含以下表格：")
    print("- users: 用户信息表")
    print("- products: 产品信息表")
    print("- orders: 订单信息表")
    print("\n你现在可以使用SQLite桌面工具打开这个数据库进行操作。")


if __name__ == "__main__":
    create_sample_database()
