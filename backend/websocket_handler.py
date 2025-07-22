import json
import asyncio
from typing import Dict, List, Optional
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Room
from auth import verify_token
from game_logic import PokerGameManager

class ConnectionManager:
    def __init__(self):
        # 存储活跃连接：{user_id: websocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # 存储房间连接：{room_id: [user_ids]}
        self.room_connections: Dict[int, List[int]] = {}
        # 游戏管理器
        self.game_manager = PokerGameManager()
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """建立WebSocket连接"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"用户 {user_id} 已连接")
    
    def disconnect(self, user_id: int):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # 从所有房间中移除用户
        for room_id, users in self.room_connections.items():
            if user_id in users:
                users.remove(user_id)
                # 如果房间中有游戏，移除玩家
                game = self.game_manager.get_game(room_id)
                if game:
                    game.remove_player(user_id)
        
        print(f"用户 {user_id} 已断开连接")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """发送个人消息"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(json.dumps(message))
            except:
                # 连接已断开，清理
                self.disconnect(user_id)
    
    async def broadcast_to_room(self, message: dict, room_id: int, exclude_user: Optional[int] = None):
        """向房间广播消息"""
        if room_id in self.room_connections:
            for user_id in self.room_connections[room_id]:
                if exclude_user and user_id == exclude_user:
                    continue
                await self.send_personal_message(message, user_id)
    
    async def join_room(self, user_id: int, room_id: int, username: str, chips: int):
        """加入房间"""
        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
        
        if user_id not in self.room_connections[room_id]:
            self.room_connections[room_id].append(user_id)
        
        # 获取或创建游戏
        game = self.game_manager.get_game(room_id)
        if not game:
            # 这里应该从数据库获取房间信息
            game = self.game_manager.create_game(room_id, 10, 20)  # 默认盲注
        
        # 添加玩家到游戏，自动分配座位位置
        # 找到第一个可用的座位位置（0-8）
        available_position = None
        occupied_positions = {p.position for p in game.players if p.position >= 0}
        for pos in range(9):  # 最多9个座位
            if pos not in occupied_positions:
                available_position = pos
                break
        
        success = game.add_player(user_id, username, chips, available_position)
        
        if success:
            # 通知房间内其他玩家
            await self.broadcast_to_room({
                "type": "player_joined",
                "data": {
                    "user_id": user_id,
                    "username": username,
                    "chips": chips
                }
            }, room_id, exclude_user=user_id)
            
            # 发送游戏状态给新玩家
            await self.send_personal_message({
                "type": "game_state",
                "data": game.get_game_state(user_id)
            }, user_id)
            
            return True
        
        return False
    
    async def leave_room(self, user_id: int, room_id: int):
        """离开房间"""
        if room_id in self.room_connections and user_id in self.room_connections[room_id]:
            self.room_connections[room_id].remove(user_id)
            
            # 从游戏中移除玩家
            game = self.game_manager.get_game(room_id)
            if game:
                game.remove_player(user_id)
                
                # 通知房间内其他玩家
                await self.broadcast_to_room({
                    "type": "player_left",
                    "data": {
                        "user_id": user_id
                    }
                }, room_id)
                
                # 广播更新的游戏状态
                await self.broadcast_game_state(room_id)
    
    async def handle_game_action(self, user_id: int, room_id: int, action: str, amount: int = 0):
        """处理游戏动作"""
        game = self.game_manager.get_game(room_id)
        if not game:
            await self.send_personal_message({
                "type": "error",
                "data": {"message": "游戏不存在"}
            }, user_id)
            return
        
        # 记录动作前的游戏阶段
        previous_stage = game.game_stage
        
        # 执行游戏动作
        result = game.player_action(user_id, action, amount)
        
        # 添加操作者信息到结果中
        result["player_id"] = user_id
        result["action"] = action
        result["amount"] = amount
        
        if result.get("success", False):
            # 成功的操作广播给所有玩家
            await self.broadcast_to_room({
                "type": "game_action",
                "data": result
            }, room_id)
            
            # 检查游戏阶段是否发生变化
            stage_changed = game.game_stage != previous_stage
            
            # 添加延迟以避免状态更新过于频繁
            if stage_changed:
                # 如果游戏阶段发生变化，稍微延迟后广播状态
                await asyncio.sleep(0.1)
            
            # 广播更新的游戏状态
            await self.broadcast_game_state(room_id)
        else:
            # 失败的操作只发送给操作者
            await self.send_personal_message({
                "type": "game_action",
                "data": result
            }, user_id)
    
    async def start_game(self, user_id: int, room_id: int):
        """开始游戏"""
        game = self.game_manager.get_game(room_id)
        if not game:
            return
        
        success = game.start_game()
        if success:
            await self.broadcast_to_room({
                "type": "game_started",
                "data": {"message": "游戏开始！"}
            }, room_id)
            
            # 广播游戏状态
            await self.broadcast_game_state(room_id)
        else:
            await self.send_personal_message({
                "type": "error",
                "data": {"message": "无法开始游戏，玩家数量不足"}
            }, user_id)
    
    async def broadcast_game_state(self, room_id: int):
        """广播游戏状态给房间内所有玩家"""
        game = self.game_manager.get_game(room_id)
        if not game:
            return
        
        if room_id in self.room_connections:
            for user_id in self.room_connections[room_id]:
                game_state = game.get_game_state(user_id)
                await self.send_personal_message({
                    "type": "game_state",
                    "data": game_state
                }, user_id)
            
            # 如果游戏结束且有游戏结果数据，广播游戏结果
            if game.game_stage == "finished" and game.game_results:
                await self.broadcast_to_room({
                    "type": "game_results",
                    "data": game.game_results
                }, room_id)
                
                # 延迟3秒后重置游戏状态为waiting
                asyncio.create_task(self._delayed_reset_game_state(room_id))
    
    async def _delayed_reset_game_state(self, room_id: int):
        """延迟重置游戏状态为waiting"""
        await asyncio.sleep(8)  # 等待3秒
        
        game = self.game_manager.get_game(room_id)
        if game and game.game_stage == "finished":
            # 重置游戏状态
            game._reset_all_players_ready_status()
            
            # 重新广播游戏状态
            await self.broadcast_game_state(room_id)
    
    async def set_player_ready(self, user_id: int, room_id: int, ready: bool):
        """设置玩家准备状态"""
        game = self.game_manager.get_game(room_id)
        if not game:
            await self.send_personal_message({
                "type": "error",
                "data": {"message": "游戏不存在"}
            }, user_id)
            return
        
        # 设置玩家准备状态
        success = game.set_player_ready(user_id, ready)
        if not success:
            await self.send_personal_message({
                "type": "error",
                "data": {"message": "设置准备状态失败"}
            }, user_id)
            return
        
        # 广播玩家准备状态变化
        await self.broadcast_to_room({
            "type": "player_ready_changed",
            "data": {
                "user_id": user_id,
                "ready": ready
            }
        }, room_id)
        
        # 检查是否需要自动开始游戏
        game_started = False
        if ready and game.game_stage == "waiting":
            all_ready = all(p.is_ready for p in game.players)
            if all_ready and len(game.players) >= 2:
                # 实际启动游戏逻辑
                start_success = game.start_game()
                if start_success:
                    game_started = True
                    # 自动开始游戏
                    await self.broadcast_to_room({
                        "type": "game_started",
                        "data": {"message": "所有玩家已准备，游戏开始！"}
                    }, room_id)
        
        # 统一广播游戏状态（无论游戏是否开始都只广播一次）
        await self.broadcast_game_state(room_id)
    
    async def send_chat_message(self, user_id: int, room_id: int, message: str, username: str):
        """发送聊天消息"""
        chat_data = {
            "type": "chat_message",
            "data": {
                "user_id": user_id,
                "username": username,
                "message": message,
                "timestamp": asyncio.get_event_loop().time()
            }
        }
        
        await self.broadcast_to_room(chat_data, room_id)
    
    async def show_player_cards(self, user_id: int, room_id: int, username: str):
        """展示玩家手牌"""
        game = self.game_manager.get_game(room_id)
        if not game:
            await self.send_personal_message({
                "type": "error",
                "data": {"message": "游戏不存在"}
            }, user_id)
            return
        
        # 找到玩家
        player = None
        for p in game.players:
            if p.user_id == user_id:
                player = p
                break
        
        if not player or not player.hole_cards:
            await self.send_personal_message({
                "type": "error",
                "data": {"message": "没有手牌可展示"}
            }, user_id)
            return
        
        # 构建手牌信息
        cards_info = []
        for card in player.hole_cards:
            card_dict = card.to_dict()
            cards_info.append(card_dict)
        
        # 广播展示手牌消息
        await self.broadcast_to_room({
            "type": "show_cards",
            "data": {
                "player_id": user_id,
                "username": username,
                "cards": cards_info
            }
        }, room_id)
        
        # 发送聊天消息通知
        card_text = ""
        for card in player.hole_cards:
            rank_str = {
                11: 'J', 12: 'Q', 13: 'K', 14: 'A'
            }.get(card.rank.value, str(card.rank.value))
            card_text += f"{rank_str}{card.suit.value} "
        
        await self.send_chat_message(user_id, room_id, f"展示了手牌：{card_text.strip()}", username)

# 全局连接管理器实例
manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """WebSocket端点"""
    # 验证token
    username = verify_token(token)
    if not username:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    # 获取用户信息
    user = db.query(User).filter(User.username == username).first()
    if not user:
        await websocket.close(code=4002, reason="User not found")
        return
    
    # 建立连接
    await manager.connect(websocket, user.id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            message_data = message.get("data", {})
            
            if message_type == "join_room":
                room_id = message_data.get("room_id")
                if room_id:
                    await manager.join_room(user.id, room_id, user.username, user.chips)
            
            elif message_type == "leave_room":
                room_id = message_data.get("room_id")
                if room_id:
                    await manager.leave_room(user.id, room_id)
            
            elif message_type == "game_action":
                room_id = message_data.get("room_id")
                action = message_data.get("action")
                amount = message_data.get("amount", 0)
                if room_id and action:
                    await manager.handle_game_action(user.id, room_id, action, amount)
            
            elif message_type == "start_game":
                room_id = message_data.get("room_id")
                if room_id:
                    await manager.start_game(user.id, room_id)
            
            elif message_type == "player_ready":
                room_id = message_data.get("room_id")
                ready = message_data.get("ready", False)
                if room_id is not None:
                    await manager.set_player_ready(user.id, room_id, ready)
            
            elif message_type == "chat":
                room_id = message_data.get("room_id")
                message_text = message_data.get("message")
                if room_id and message_text:
                    await manager.send_chat_message(user.id, room_id, message_text, user.username)
            
            elif message_type == "show_cards":
                room_id = message_data.get("room_id")
                if room_id:
                    await manager.show_player_cards(user.id, room_id, user.username)
            
            elif message_type == "ping":
                # 心跳包
                await manager.send_personal_message({
                    "type": "pong",
                    "data": {}
                }, user.id)
    
    except WebSocketDisconnect:
        manager.disconnect(user.id)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        manager.disconnect(user.id)