from fastapi import FastAPI, HTTPException, Depends, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import get_db, engine, Base
from models import User, Room, Game, Transaction, BorrowRecord, SystemConfig, RoomStatus
from schemas import (
    UserCreate, UserLogin, UserResponse, UserUpdate,
    RoomCreate, RoomResponse,
    TransactionCreate, TransactionResponse,
    BorrowRequest, BorrowResponse,
    SystemConfigUpdate
)
from auth import get_password_hash, authenticate_user, create_access_token, get_current_user, verify_token
from websocket_handler import websocket_endpoint, manager

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="德州扑克游戏后端", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
# game_manager将从websocket_handler导入，确保使用同一个实例

# 用户认证相关接口
@app.post("/api/auth/register", response_model=dict)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        chips=1000,  # 初始筹码
        borrow_count=3,  # 初始借码次数
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"success": True, "message": "注册成功"}

@app.post("/api/auth/login", response_model=dict)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "success": True,
        "token": access_token,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "avatar": user.avatar or "https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=poker%20player%20avatar&image_size=square",
            "chips": user.chips,
            "borrow_count": user.borrow_count,
            "level": user.level,
            "win_rate": user.win_rate,
            "total_games": user.total_games,
            "is_admin": user.is_admin
        }
    }

@app.get("/api/user/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        avatar=current_user.avatar or "https://trae-api-sg.mchost.guru/api/ide/v1/text_to_image?prompt=poker%20player%20avatar&image_size=square",
        chips=current_user.chips,
        borrow_count=current_user.borrow_count,
        level=current_user.level,
        win_rate=current_user.win_rate,
        total_games=current_user.total_games,
        is_admin=current_user.is_admin
    )

# 借码相关接口
@app.post("/api/user/borrow", response_model=BorrowResponse)
async def borrow_chips(
    borrow_data: BorrowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查借码条件
    if current_user.borrow_count <= 0:
        raise HTTPException(status_code=400, detail="借码次数已用完")
    
    # 获取系统配置的单次借码数量
    config = db.query(SystemConfig).filter(SystemConfig.key == "borrow_amount").first()
    borrow_amount = int(config.value) if config else 1000
    
    # 检查是否满足借码条件（余额为0或小于等于大盲注）
    big_blind = borrow_data.big_blind or 20  # 默认大盲注
    if current_user.chips > big_blind:
        raise HTTPException(status_code=400, detail="余额充足，无需借码")
    
    # 执行借码
    current_user.chips += borrow_amount
    current_user.borrow_count -= 1
    
    # 记录借码记录
    borrow_record = BorrowRecord(
        user_id=current_user.id,
        amount=borrow_amount,
        remaining_count=current_user.borrow_count
    )
    
    db.add(borrow_record)
    db.commit()
    db.refresh(current_user)
    
    return BorrowResponse(
        success=True,
        message=f"借码成功，获得{borrow_amount}筹码",
        new_chips=current_user.chips,
        remaining_borrow_count=current_user.borrow_count
    )

# 充值相关接口（后台审批制）
@app.post("/api/user/recharge", response_model=dict)
async def create_recharge_request(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 创建充值申请记录
    transaction = Transaction(
        user_id=current_user.id,
        amount=transaction_data.amount,
        transaction_type="recharge",
        status="pending",
        description=f"用户{current_user.username}申请充值{transaction_data.amount}筹码"
    )
    
    db.add(transaction)
    db.commit()
    
    return {
        "success": True,
        "message": "充值申请已提交，等待管理员审批",
        "transaction_id": transaction.id
    }

@app.get("/api/user/transactions", response_model=List[TransactionResponse])
async def get_user_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).limit(20).all()
    
    return [TransactionResponse(
        id=t.id,
        amount=t.amount,
        transaction_type=t.transaction_type,
        status=t.status,
        description=t.description,
        created_at=t.created_at
    ) for t in transactions]

# 管理员接口
@app.get("/api/admin/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
    
    users = db.query(User).all()
    return [UserResponse(
        id=str(u.id),
        username=u.username,
        avatar=u.avatar,
        chips=u.chips,
        borrow_count=u.borrow_count,
        level=u.level,
        win_rate=u.win_rate,
        total_games=u.total_games,
        is_admin=u.is_admin
    ) for u in users]

@app.post("/api/admin/approve-recharge/{transaction_id}")
async def approve_recharge(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
    
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="交易记录不存在")
    
    if transaction.status != "pending":
        raise HTTPException(status_code=400, detail="该交易已处理")
    
    # 审批通过，增加用户筹码
    user = db.query(User).filter(User.id == transaction.user_id).first()
    user.chips += transaction.amount
    transaction.status = "approved"
    transaction.description += f" - 管理员{current_user.username}审批通过"
    
    db.commit()
    
    return {"success": True, "message": "充值审批成功"}

@app.post("/api/admin/config/borrow-amount")
async def set_borrow_amount(
    config_data: SystemConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足")
    
    config = db.query(SystemConfig).filter(SystemConfig.key == "borrow_amount").first()
    if config:
        config.value = str(config_data.value)
    else:
        config = SystemConfig(key="borrow_amount", value=str(config_data.value))
        db.add(config)
    
    db.commit()
    
    return {"success": True, "message": f"单次借码数量已设置为{config_data.value}"}

# 房间管理接口
@app.get("/api/rooms", response_model=List[RoomResponse])
async def get_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).filter(Room.status != "finished").all()
    return [RoomResponse(
        id=r.id,
        name=r.name,
        small_blind=r.small_blind,
        big_blind=r.big_blind,
        max_players=r.max_players,
        current_players=r.current_players,
        status=r.status.value,
        created_at=r.created_at
    ) for r in rooms]

@app.post("/api/rooms", response_model=RoomResponse)
async def create_room(
    room_data: RoomCreate,
    db: Session = Depends(get_db)
):
    new_room = Room(
        name=room_data.name,
        small_blind=room_data.small_blind,
        big_blind=room_data.big_blind,
        max_players=room_data.max_players,
        created_by=None  # 不再需要用户认证
    )
    
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    
    return RoomResponse(
        id=new_room.id,
        name=new_room.name,
        small_blind=new_room.small_blind,
        big_blind=new_room.big_blind,
        max_players=new_room.max_players,
        current_players=new_room.current_players,
        status=new_room.status.value,
        created_at=new_room.created_at
    )

@app.get("/api/rooms/{room_id}", response_model=RoomResponse)
async def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    return RoomResponse(
        id=room.id,
        name=room.name,
        small_blind=room.small_blind,
        big_blind=room.big_blind,
        max_players=room.max_players,
        current_players=room.current_players,
        status=room.status.value,
        created_at=room.created_at
    )

@app.delete("/api/rooms/{room_id}")
async def delete_room(
    room_id: int,
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    # 检查房间是否有玩家
    if room.current_players > 0:
        raise HTTPException(status_code=400, detail="房间内还有玩家，无法删除")
    
    db.delete(room)
    db.commit()
    
    return {"success": True, "message": "房间删除成功"}

@app.post("/api/rooms/{room_id}/join")
async def join_room(
    room_id: int,
    join_data: dict,
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if room.current_players >= room.max_players:
        raise HTTPException(status_code=400, detail="房间已满")
    
    # 更新房间玩家数量
    room.current_players += 1
    if room.current_players == 1:
        room.status = RoomStatus.WAITING
    
    db.commit()
    
    return {
        "success": True,
        "message": "成功加入房间",
        "room": RoomResponse(
            id=room.id,
            name=room.name,
            small_blind=room.small_blind,
            big_blind=room.big_blind,
            max_players=room.max_players,
            current_players=room.current_players,
            status=room.status.value,
            created_at=room.created_at
        )
    }

@app.post("/api/rooms/{room_id}/leave")
async def leave_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    # 从游戏中移除玩家
    game = manager.game_manager.get_game(room_id)
    if game:
        game.remove_player(current_user.id)
        # 更新房间玩家数量为实际游戏中的玩家数
        room.current_players = len(game.players)
    else:
        # 如果没有游戏实例，直接减少玩家数
        if room.current_players > 0:
            room.current_players -= 1
    
    if room.current_players == 0:
        room.status = RoomStatus.WAITING
    
    db.commit()
    
    return {"success": True, "message": "成功离开房间"}

@app.get("/api/rooms/{room_id}/game-state")
async def get_game_state(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取房间的游戏状态"""
    print(f"[DEBUG API] get_game_state called: room_id={room_id}, user_id={current_user.id}")
    
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        print(f"[DEBUG API] Room not found for room_id: {room_id}")
        raise HTTPException(status_code=404, detail="房间不存在")
    
    # 获取游戏实例
    game = manager.game_manager.get_game(room_id)
    
    if not game:
        # 如果游戏不存在，创建一个新游戏
        print(f"[DEBUG API] Creating new game for room_id: {room_id}")
        game = manager.game_manager.create_game(room_id, room.small_blind, room.big_blind)
    
    # 同步房间的current_players字段与实际游戏中的玩家数量
    actual_players = len(game.players)
    if room.current_players != actual_players:
        room.current_players = actual_players
        db.commit()
    
    # 获取游戏状态
    game_state = game.get_game_state(current_user.id)
    print(f"[DEBUG API] Game state players: {[(p['user_id'], p['position']) for p in game_state.get('players', [])]}")
    
    return {
        "success": True,
        "room": {
            "id": room.id,
            "name": room.name,
            "small_blind": room.small_blind,
            "big_blind": room.big_blind,
            "max_players": room.max_players,
            "current_players": actual_players,
            "status": room.status.value
        },
        "game": {
            "id": str(room_id),
            "players": game_state.get("players", []),
            "communityCards": game_state.get("community_cards", []),
            "pot": game_state.get("pot", 0),
            "currentBet": game_state.get("current_bet", 0),
            "current_player": game_state.get("current_player"),
            "currentPlayerIndex": next((i for i, p in enumerate(game_state.get("players", [])) if p.get("user_id") == game_state.get("current_player")), 0),
            "phase": game_state.get("stage", "waiting"),
            "smallBlind": room.small_blind,
            "bigBlind": room.big_blind,
            "dealerPosition": 0
        }
     }

@app.post("/api/rooms/{room_id}/join-game")
async def join_game(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """加入游戏"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    # 获取或创建游戏实例
    game = manager.game_manager.get_game(room_id)
    if not game:
        game = manager.game_manager.create_game(room_id, room.small_blind, room.big_blind)
    
    # 检查玩家是否已经在游戏中
    existing_player = game._get_player_by_id(current_user.id)
    if existing_player:
        return {
            "success": True,
            "message": "已在游戏中",
            "game_state": game.get_game_state(current_user.id)
        }
    
    # 添加玩家到游戏，不指定位置（让前端通过change-seat选择）
    success = game.add_player(current_user.id, current_user.username, current_user.chips)
    if not success:
        raise HTTPException(status_code=400, detail="游戏已满或无法加入")
    
    # 更新房间的current_players字段以反映实际游戏中的玩家数量
    room.current_players = len(game.players)
    db.commit()
    
    return {
        "success": True,
        "message": "成功加入游戏",
        "game_state": game.get_game_state(current_user.id)
    }

@app.post("/api/rooms/{room_id}/ready")
async def set_player_ready(
    room_id: int,
    ready_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设置玩家准备状态"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    # 获取游戏实例
    game = manager.game_manager.get_game(room_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    # 记录设置前的游戏状态
    was_waiting = game.game_stage == "waiting"
    
    # 设置玩家准备状态
    ready = ready_data.get("ready", False)
    success = game.set_player_ready(current_user.id, ready)
    
    if not success:
        raise HTTPException(status_code=400, detail="设置准备状态失败")
    
    # 广播玩家准备状态变化
    await manager.broadcast_to_room({
        "type": "player_ready_changed",
        "data": {
            "user_id": current_user.id,
            "ready": ready
        }
    }, room_id)
    
    # 检查游戏是否已经自动开始
    if was_waiting and game.game_stage != "waiting":
        # 游戏已经自动开始，广播游戏开始消息
        await manager.broadcast_to_room({
            "type": "game_started",
            "data": {"message": "所有玩家已准备，游戏开始！"}
        }, room_id)
    
    # 广播游戏状态更新到WebSocket
    await manager.broadcast_game_state(room_id)
    
    return {
        "success": True,
        "message": f"玩家{'准备' if ready else '取消准备'}成功",
        "ready": ready
    }

@app.post("/api/rooms/{room_id}/change-seat")
async def change_seat(
    room_id: int,
    seat_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """切换座位"""
    print(f"[DEBUG API] change_seat endpoint called: room_id={room_id}, user_id={current_user.id}, seat_data={seat_data}")
    
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        print(f"[DEBUG API] Room not found for room_id: {room_id}")
        raise HTTPException(status_code=404, detail="房间不存在")
    
    # 获取游戏实例
    game = manager.game_manager.get_game(room_id)
    if not game:
        print(f"[DEBUG API] Game not found for room_id: {room_id}")
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    # 切换座位
    seat_index = seat_data.get("seat_index")
    if seat_index is None:
        print(f"[DEBUG API] Seat index is None")
        raise HTTPException(status_code=400, detail="座位索引不能为空")
    
    print(f"[DEBUG API] Game found, calling change_player_seat with user_id={current_user.id}, seat_index={seat_index}")
    success = game.change_player_seat(current_user.id, seat_index)
    
    if not success:
        print(f"[DEBUG API] Seat change failed")
        raise HTTPException(status_code=400, detail="切换座位失败，座位可能已被占用")
    
    print(f"[DEBUG API] Seat change successful")
    return {
        "success": True,
        "message": f"成功切换到座位{seat_index + 1}",
        "seat_index": seat_index
    }

@app.post("/api/rooms/{room_id}/start-game")
async def start_game(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """开始新游戏"""
    print(f"[DEBUG API] start_game endpoint called: room_id={room_id}, user_id={current_user.id}")
    
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        print(f"[DEBUG API] Room not found for room_id: {room_id}")
        raise HTTPException(status_code=404, detail="房间不存在")
    
    # 获取游戏实例
    game = manager.game_manager.get_game(room_id)
    if not game:
        print(f"[DEBUG API] Game not found for room_id: {room_id}")
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    # 调用开始游戏方法
    print(f"[DEBUG API] Calling start_game method")
    success = game.start_game()
    
    if success:
        print(f"[DEBUG API] Game started successfully")
        # 广播游戏开始消息
        await manager.broadcast_to_room({
            "type": "game_started",
            "data": {"message": "游戏开始！"}
        }, room_id)
        
        # 广播游戏状态
        await manager.broadcast_game_state(room_id)
        
        return {
            "success": True,
            "message": "游戏开始成功",
            "game_state": game.get_game_state(current_user.id)
        }
    else:
        print(f"[DEBUG API] Game start failed")
        raise HTTPException(status_code=400, detail="无法开始游戏，玩家数量不足或游戏已在进行中")

# WebSocket路由
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    await websocket_endpoint(websocket, token, db)

# 根路径
@app.get("/")
async def root():
    return {"message": "德州扑克游戏后端API", "version": "1.0.0", "status": "running"}

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "德州扑克游戏后端运行正常"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)