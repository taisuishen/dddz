from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# 用户相关模式
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    avatar: Optional[str] = None
    chips: int
    borrow_count: int
    level: int
    win_rate: float
    total_games: int
    is_admin: bool
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    avatar: Optional[str] = None
    chips: Optional[int] = None
    borrow_count: Optional[int] = None
    is_active: Optional[bool] = None

# 房间相关模式
class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    small_blind: int = Field(default=10, ge=1)
    big_blind: int = Field(default=20, ge=2)
    max_players: int = Field(default=9, ge=2, le=9)

class RoomResponse(BaseModel):
    id: int
    name: str
    small_blind: int
    big_blind: int
    max_players: int
    current_players: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# 游戏相关模式
class GameAction(BaseModel):
    action: str  # fold, call, raise, check, all_in
    amount: Optional[int] = None  # 加注金额

class GameState(BaseModel):
    game_id: int
    status: str
    pot: int
    community_cards: Optional[List[str]] = None
    current_player: Optional[int] = None
    players: List[dict]
    
    class Config:
        from_attributes = True

# 交易相关模式
class TransactionCreate(BaseModel):
    amount: int = Field(..., gt=0)
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    amount: int
    transaction_type: str
    status: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# 借码相关模式
class BorrowRequest(BaseModel):
    big_blind: Optional[int] = 20  # 当前房间的大盲注

class BorrowResponse(BaseModel):
    success: bool
    message: str
    new_chips: int
    remaining_borrow_count: int

# 系统配置相关模式
class SystemConfigUpdate(BaseModel):
    value: int = Field(..., gt=0)

class SystemConfigResponse(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

# WebSocket消息模式
class WSMessage(BaseModel):
    type: str  # join_room, leave_room, game_action, game_state, chat
    data: dict

class ChatMessage(BaseModel):
    user_id: int
    username: str
    message: str
    timestamp: datetime

# 统计相关模式
class UserStats(BaseModel):
    total_games: int
    wins: int
    losses: int
    win_rate: float
    total_chips_won: int
    total_chips_lost: int
    
class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_games: int
    active_rooms: int
    pending_transactions: int
    total_chips_in_system: int