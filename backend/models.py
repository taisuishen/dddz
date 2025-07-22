from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    avatar = Column(String(500), nullable=True)
    chips = Column(Integer, default=1000)  # 筹码余额
    borrow_count = Column(Integer, default=3)  # 借码次数
    level = Column(Integer, default=1)  # 用户等级
    win_rate = Column(Float, default=0.0)  # 胜率
    total_games = Column(Integer, default=0)  # 总游戏数
    is_admin = Column(Boolean, default=False)  # 是否管理员
    is_active = Column(Boolean, default=True)  # 账户是否激活
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    transactions = relationship("Transaction", back_populates="user", foreign_keys="Transaction.user_id")
    borrow_records = relationship("BorrowRecord", back_populates="user")
    game_participations = relationship("GameParticipation", back_populates="user")

class RoomStatus(enum.Enum):
    WAITING = "waiting"  # 等待中
    PLAYING = "playing"  # 游戏中
    FINISHED = "finished"  # 已结束

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    small_blind = Column(Integer, default=10)  # 小盲注
    big_blind = Column(Integer, default=20)  # 大盲注
    max_players = Column(Integer, default=9)  # 最大玩家数
    current_players = Column(Integer, default=0)  # 当前玩家数
    status = Column(Enum(RoomStatus), default=RoomStatus.WAITING)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    creator = relationship("User")
    games = relationship("Game", back_populates="room")

class GameStatus(enum.Enum):
    WAITING = "waiting"  # 等待开始
    PREFLOP = "preflop"  # 翻牌前
    FLOP = "flop"  # 翻牌
    TURN = "turn"  # 转牌
    RIVER = "river"  # 河牌
    SHOWDOWN = "showdown"  # 摊牌
    FINISHED = "finished"  # 结束

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    status = Column(Enum(GameStatus), default=GameStatus.WAITING)
    pot = Column(Integer, default=0)  # 底池
    community_cards = Column(String(50), nullable=True)  # 公共牌
    current_player = Column(Integer, nullable=True)  # 当前行动玩家
    dealer_position = Column(Integer, default=0)  # 庄家位置
    small_blind_position = Column(Integer, default=1)  # 小盲位置
    big_blind_position = Column(Integer, default=2)  # 大盲位置
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    
    # 关系
    room = relationship("Room", back_populates="games")
    participations = relationship("GameParticipation", back_populates="game")

class GameParticipation(Base):
    __tablename__ = "game_participations"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    position = Column(Integer, nullable=False)  # 座位位置
    hole_cards = Column(String(10), nullable=True)  # 手牌
    chips_at_start = Column(Integer, nullable=False)  # 开始时筹码
    chips_at_end = Column(Integer, nullable=True)  # 结束时筹码
    is_folded = Column(Boolean, default=False)  # 是否弃牌
    is_all_in = Column(Boolean, default=False)  # 是否全下
    total_bet = Column(Integer, default=0)  # 总下注额
    
    # 关系
    game = relationship("Game", back_populates="participations")
    user = relationship("User", back_populates="game_participations")

class TransactionType(enum.Enum):
    RECHARGE = "recharge"  # 充值
    WITHDRAW = "withdraw"  # 提现
    GAME_WIN = "game_win"  # 游戏获胜
    GAME_LOSS = "game_loss"  # 游戏失败
    BORROW = "borrow"  # 借码

class TransactionStatus(enum.Enum):
    PENDING = "pending"  # 待处理
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    COMPLETED = "completed"  # 已完成

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer, nullable=False)  # 金额
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(Text, nullable=True)  # 描述
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 处理人
    
    # 关系
    user = relationship("User", back_populates="transactions", foreign_keys=[user_id])
    processor = relationship("User", foreign_keys=[processed_by])

class BorrowRecord(Base):
    __tablename__ = "borrow_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer, nullable=False)  # 借码金额
    remaining_count = Column(Integer, nullable=False)  # 剩余借码次数
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="borrow_records")

class SystemConfig(Base):
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)  # 配置键
    value = Column(Text, nullable=False)  # 配置值
    description = Column(Text, nullable=True)  # 描述
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)