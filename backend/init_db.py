#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""

from database import engine, Base, SessionLocal
from models import User, Room, Game, Transaction, BorrowRecord, SystemConfig
from auth import get_password_hash
import os

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    # 删除现有数据库文件（如果存在）
    db_file = "poker_game.db"
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"已删除现有数据库文件: {db_file}")
        except Exception as e:
            print(f"删除数据库文件失败: {e}")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")
    
    # 创建会话
    db = SessionLocal()
    
    try:
        # 创建默认管理员用户
        admin_user = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            chips=10000,
            borrow_count=3,
            is_admin=True,
            is_active=True
        )
        db.add(admin_user)
        
        # 创建测试用户
        test_user = User(
            username="player1",
            hashed_password=get_password_hash("123456"),
            chips=1000,
            borrow_count=3,
            is_admin=False,
            is_active=True
        )
        db.add(test_user)
        
        # 创建系统配置
        borrow_config = SystemConfig(
            key="borrow_amount",
            value="1000",
            description="单次借码数量"
        )
        db.add(borrow_config)
        
        # 提交更改
        db.commit()
        print("默认数据创建完成")
        print("管理员账户: admin / admin123")
        print("测试账户: player1 / 123456")
        
    except Exception as e:
        print(f"创建默认数据失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    print("数据库初始化完成！")