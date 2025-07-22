import random
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import itertools

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class HandRank(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

@dataclass
class Card:
    suit: Suit
    rank: Rank
    
    def __str__(self):
        rank_str = {
            11: 'J', 12: 'Q', 13: 'K', 14: 'A'
        }.get(self.rank.value, str(self.rank.value))
        return f"{rank_str}{self.suit.value}"
    
    def to_dict(self):
        return {
            'suit': self.suit.value,
            'rank': self.rank.value,
            'display': str(self)
        }

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        """重置并洗牌"""
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank]
        self.shuffle()
    
    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)
    
    def deal_card(self) -> Optional[Card]:
        """发一张牌"""
        return self.cards.pop() if self.cards else None
    
    def deal_cards(self, count: int) -> List[Card]:
        """发多张牌"""
        return [self.deal_card() for _ in range(count) if self.cards]

class Player:
    def __init__(self, user_id: int, username: str, chips: int, position: int):
        self.user_id = user_id
        self.username = username
        self.chips = chips
        self.position = position
        self.hole_cards: List[Card] = []
        self.current_bet = 0
        self.total_bet = 0
        self.is_folded = False
        self.is_all_in = False
        self.is_active = True
        self.is_ready = False
        self.has_acted_this_round = False
    
    def bet(self, amount: int) -> int:
        """下注"""
        actual_bet = min(amount, self.chips)
        self.chips -= actual_bet
        self.current_bet += actual_bet
        self.total_bet += actual_bet
        
        if self.chips == 0:
            self.is_all_in = True
        
        return actual_bet
    
    def fold(self):
        """弃牌"""
        self.is_folded = True
        self.is_active = False
    
    def reset_for_new_round(self):
        """新一轮重置"""
        self.current_bet = 0
        self.has_acted_this_round = False
    
    def to_dict(self, show_hole_cards: bool = False):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'chips': self.chips,
            'position': self.position,
            'current_bet': self.current_bet,
            'total_bet': self.total_bet,
            'is_folded': self.is_folded,
            'is_all_in': self.is_all_in,
            'is_active': self.is_active,
            'is_ready': self.is_ready,
            'hole_cards': [card.to_dict() for card in self.hole_cards] if show_hole_cards else []
        }

class HandEvaluator:
    @staticmethod
    def evaluate_hand(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """评估手牌强度"""
        if len(cards) < 5:
            return HandRank.HIGH_CARD, []
        
        # 获取所有可能的5张牌组合
        best_hand = None
        best_rank = HandRank.HIGH_CARD
        best_values = []
        
        for combo in itertools.combinations(cards, 5):
            rank, values = HandEvaluator._evaluate_five_cards(list(combo))
            if rank.value > best_rank.value or (rank == best_rank and values > best_values):
                best_hand = combo
                best_rank = rank
                best_values = values
        
        return best_rank, best_values
    
    @staticmethod
    def _evaluate_five_cards(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """评估5张牌的组合"""
        ranks = sorted([card.rank.value for card in cards], reverse=True)
        suits = [card.suit for card in cards]
        
        # 检查是否为同花
        is_flush = len(set(suits)) == 1
        
        # 检查是否为顺子
        is_straight = HandEvaluator._is_straight(ranks)
        
        # 统计每个点数的出现次数
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        counts = sorted(rank_counts.values(), reverse=True)
        unique_ranks = sorted(rank_counts.keys(), key=lambda x: (rank_counts[x], x), reverse=True)
        
        # 判断牌型
        if is_straight and is_flush:
            if ranks == [14, 13, 12, 11, 10]:  # 皇家同花顺
                return HandRank.ROYAL_FLUSH, ranks
            else:  # 同花顺
                return HandRank.STRAIGHT_FLUSH, ranks
        elif counts == [4, 1]:  # 四条
            return HandRank.FOUR_OF_A_KIND, unique_ranks
        elif counts == [3, 2]:  # 葫芦
            return HandRank.FULL_HOUSE, unique_ranks
        elif is_flush:  # 同花
            return HandRank.FLUSH, ranks
        elif is_straight:  # 顺子
            return HandRank.STRAIGHT, ranks
        elif counts == [3, 1, 1]:  # 三条
            return HandRank.THREE_OF_A_KIND, unique_ranks
        elif counts == [2, 2, 1]:  # 两对
            return HandRank.TWO_PAIR, unique_ranks
        elif counts == [2, 1, 1, 1]:  # 一对
            return HandRank.PAIR, unique_ranks
        else:  # 高牌
            return HandRank.HIGH_CARD, ranks
    
    @staticmethod
    def _is_straight(ranks: List[int]) -> bool:
        """检查是否为顺子"""
        ranks = sorted(set(ranks))
        if len(ranks) != 5:
            return False
        
        # 普通顺子
        if ranks[-1] - ranks[0] == 4:
            return True
        
        # A-2-3-4-5 顺子
        if ranks == [2, 3, 4, 5, 14]:
            return True
        
        return False

class PokerGame:
    def __init__(self, room_id: int, small_blind: int, big_blind: int):
        self.room_id = room_id
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.players: List[Player] = []
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_bet = 0
        self.current_player_index = 0
        self.dealer_position = 0  # 初始庄家位置，会在第一次开始游戏时设置
        self.game_stage = "waiting"  # waiting, preflop, flop, turn, river, showdown
        self.is_finished = False
        self.side_pots: List[Dict] = []
        self.game_results: Optional[Dict] = None
        self._first_game = True  # 标记是否是第一局游戏
    
    def add_player(self, user_id: int, username: str, chips: int, position: int = None) -> bool:
        """添加玩家"""
        if len(self.players) >= 9:
            return False
        
        # 检查用户是否已存在
        for p in self.players:
            if p.user_id == user_id:
                return True  # 用户已存在，直接返回成功
        
        # 如果没有指定位置，设置为-1（表示未选择座位）
        if position is None:
            position = -1
        else:
            # 检查指定位置是否已被占用
            for p in self.players:
                if p.position == position:
                    return False
        
        player = Player(user_id, username, chips, position)
        self.players.append(player)
        # 按位置排序玩家列表，-1的玩家排在最后
        self.players.sort(key=lambda p: (p.position if p.position >= 0 else 999, p.user_id))
        return True
    
    def remove_player(self, user_id: int) -> bool:
        """移除玩家"""
        for i, player in enumerate(self.players):
            if player.user_id == user_id:
                self.players.pop(i)
                # 不重新分配位置，保持其他玩家的座位不变
                return True
        return False
    
    def start_game(self) -> bool:
        """开始游戏"""
        if len(self.players) < 2:
            return False
        
        # 重置所有玩家状态
        for player in self.players:
            player.hole_cards = []
            player.current_bet = 0
            player.total_bet = 0
            player.is_folded = False
            player.is_all_in = False
            player.is_active = True
            player.has_acted_this_round = False
        
        # 如果是第一局游戏，设置庄家位置为第一个玩家
        if self._first_game and self.players:
            self.dealer_position = self.players[0].position
            self._first_game = False
            print(f"[DEBUG] First game: dealer_position set to {self.dealer_position}")
        
        # 重置游戏状态
        self.deck.reset()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.game_stage = "preflop"
        self.is_finished = False
        self.game_results = None
        
        print(f"[DEBUG] start_game: game_stage={self.game_stage}")
        print(f"[DEBUG] start_game: dealer_position={self.dealer_position}")
        
        # 发手牌
        for _ in range(2):
            for player in self.players:
                if not player.is_folded:
                    card = self.deck.deal_card()
                    if card:
                        player.hole_cards.append(card)
        
        # 下盲注
        self._post_blinds()
        
        # 设置第一个行动玩家（大盲注后的第一个玩家）
        # 在preflop阶段，第一个行动玩家是大盲注左边的玩家
        # 注意：这里需要基于数组索引，而不是position
        
        # 找到庄家在数组中的索引
        dealer_array_index = None
        for i, player in enumerate(self.players):
            if player.position == self.dealer_position:
                dealer_array_index = i
                break
        
        if dealer_array_index is not None:
            if len(self.players) == 2:
                # 两人游戏：大盲注是庄家后第1个玩家，大盲右边的第一个玩家就是庄家（小盲）
                # 所以小盲注玩家（庄家）先行动
                big_blind_array_index = (dealer_array_index + 1) % len(self.players)
                self.current_player_index = (big_blind_array_index + 1) % len(self.players)
            else:
                # 多人游戏：大盲注是庄家后第2个玩家，大盲右边的第一个玩家是庄家后第3个玩家（UTG）
                big_blind_array_index = (dealer_array_index + 2) % len(self.players)
                self.current_player_index = (big_blind_array_index + 1) % len(self.players)
        else:
            # 如果找不到庄家，默认从第一个玩家开始
            self.current_player_index = 0
        
        print(f"[DEBUG] start_game: dealer_position={self.dealer_position}, dealer_array_index={dealer_array_index}")
        print(f"[DEBUG] start_game: current_player_index={self.current_player_index}")
        print(f"[DEBUG] start_game: players={[(p.user_id, p.position) for p in self.players]}")
        
        # 确保找到下一个活跃玩家
        self._find_next_active_player()
        
        return True
    
    def _post_blinds(self):
        """下盲注"""
        if len(self.players) >= 2:
            # 找到庄家在数组中的索引
            dealer_array_index = None
            for i, player in enumerate(self.players):
                if player.position == self.dealer_position:
                    dealer_array_index = i
                    break
            
            if dealer_array_index is not None:
                if len(self.players) == 2:
                    # 两人游戏：庄家是小盲注，另一个玩家是大盲注
                    small_blind_array_index = dealer_array_index
                    big_blind_array_index = (dealer_array_index + 1) % len(self.players)
                else:
                    # 多人游戏：庄家后第1个玩家是小盲注，第2个玩家是大盲注
                    small_blind_array_index = (dealer_array_index + 1) % len(self.players)
                    big_blind_array_index = (dealer_array_index + 2) % len(self.players)
                
                small_blind_player = self.players[small_blind_array_index]
                small_blind_amount = small_blind_player.bet(self.small_blind)
                self.pot += small_blind_amount
                
                big_blind_player = self.players[big_blind_array_index]
                big_blind_amount = big_blind_player.bet(self.big_blind)
                self.current_bet = self.big_blind
                self.pot += big_blind_amount
                
                print(f"[DEBUG] _post_blinds: dealer={dealer_array_index}, small_blind={small_blind_array_index}, big_blind={big_blind_array_index}")
                print(f"[DEBUG] Small blind: user {small_blind_player.user_id} bet {small_blind_amount}")
                print(f"[DEBUG] Big blind: user {big_blind_player.user_id} bet {big_blind_amount}")
    
    def player_action(self, user_id: int, action: str, amount: int = 0) -> Dict:
        """玩家行动"""
        player = self._get_player_by_id(user_id)
        current_player = self.players[self.current_player_index] if self.current_player_index < len(self.players) else None
        
        print(f"[DEBUG] player_action: user_id={user_id}, current_player_index={self.current_player_index}")
        print(f"[DEBUG] current_player: {current_player.user_id if current_player else None}")
        print(f"[DEBUG] players: {[(p.user_id, p.position) for p in self.players]}")
        
        if not player or player != current_player:
            return {"success": False, "message": "不是你的回合"}
        
        if player.is_folded or not player.is_active:
            return {"success": False, "message": "你已经弃牌或不在游戏中"}
        
        result = {"success": True, "action": action}
        
        # 标记玩家已在本轮行动
        player.has_acted_this_round = True
        
        if action == "fold":
            player.fold()
            result["message"] = f"{player.username} 弃牌"
            
            # 检查弃牌后是否只剩一个活跃玩家，如果是则立即结束游戏
            active_players = [p for p in self.players if p.is_active and not p.is_folded]
            if len(active_players) <= 1:
                print(f"[DEBUG] Only {len(active_players)} active players left after fold, going to showdown")
                self.game_stage = "showdown"
                self._showdown()
                return result
        
        elif action == "call":
            call_amount = self.current_bet - player.current_bet
            print(f"[DEBUG] Call calculation: current_bet={self.current_bet}, player.current_bet={player.current_bet}, call_amount={call_amount}")
            print(f"[DEBUG] Player chips before bet: {player.chips}")
            actual_bet = player.bet(call_amount)
            print(f"[DEBUG] Actual bet amount: {actual_bet}")
            print(f"[DEBUG] Player chips after bet: {player.chips}")
            self.pot += actual_bet
            result["message"] = f"{player.username} 跟注 {actual_bet}"
        
        elif action == "raise":
            if amount < self.current_bet * 2:
                return {"success": False, "message": "加注金额不足"}
            
            total_bet_needed = amount - player.current_bet
            actual_bet = player.bet(total_bet_needed)
            self.pot += actual_bet
            self.current_bet = player.current_bet
            result["message"] = f"{player.username} 加注到 {self.current_bet}"
        
        elif action == "check":
            if player.current_bet < self.current_bet:
                return {"success": False, "message": "无法过牌，需要跟注或弃牌"}
            result["message"] = f"{player.username} 过牌"
        
        elif action == "all_in":
            all_in_amount = player.chips
            actual_bet = player.bet(all_in_amount)
            self.pot += actual_bet
            if player.current_bet > self.current_bet:
                self.current_bet = player.current_bet
            result["message"] = f"{player.username} 全下 {actual_bet}"
        
        print(f"[DEBUG] player_action completed: {action} by {player.username}")
        print(f"[DEBUG] Current game state: pot={self.pot}, current_bet={self.current_bet}")
        print(f"[DEBUG] Player states: {[(p.user_id, p.chips, p.current_bet, p.is_folded, p.is_all_in) for p in self.players]}")
        
        # 移动到下一个玩家
        self._next_player()
        
        print(f"[DEBUG] After _next_player: current_player_index={self.current_player_index}")
        if self.current_player_index < len(self.players):
            print(f"[DEBUG] Next player: {self.players[self.current_player_index].user_id}")
        
        return result
    
    def _get_player_by_id(self, user_id: int) -> Optional[Player]:
        """根据用户ID获取玩家"""
        for player in self.players:
            if player.user_id == user_id:
                return player
        return None
    
    def _next_player(self):
        """移动到下一个活跃玩家"""
        start_index = self.current_player_index
        attempts = 0
        max_attempts = len(self.players)
        
        print(f"[DEBUG] _next_player: starting from index {self.current_player_index}")
        
        while attempts < max_attempts:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            current_player = self.players[self.current_player_index]
            
            print(f"[DEBUG] _next_player: moved to player {current_player.user_id} at index {self.current_player_index}")
            print(f"[DEBUG] Player state: is_active={current_player.is_active}, is_folded={current_player.is_folded}, is_all_in={current_player.is_all_in}")
            print(f"[DEBUG] Player bet state: current_bet={current_player.current_bet}, game_current_bet={self.current_bet}, has_acted={current_player.has_acted_this_round}")
            
            # 跳过已弃牌或不活跃的玩家
            if current_player.is_active and not current_player.is_folded:
                # 检查是否需要行动：如果不是all_in且下注不足，则需要行动
                if not current_player.is_all_in and current_player.current_bet < self.current_bet:
                    print(f"[DEBUG] Found next active player who needs to act: {current_player.user_id}")
                    return
                # 如果是all_in或下注已足够，但还没有在本轮行动过，也需要给机会行动（比如check）
                elif not current_player.has_acted_this_round and not current_player.is_all_in and current_player.current_bet == self.current_bet:
                    print(f"[DEBUG] Found player who can check: {current_player.user_id}")
                    return
                # 如果是all_in或已经行动过且下注足够，继续寻找下一个需要行动的玩家
                else:
                    print(f"[DEBUG] Player {current_player.user_id} doesn't need to act (all_in={current_player.is_all_in}, bet={current_player.current_bet}/{self.current_bet}, has_acted={current_player.has_acted_this_round})")
            
            attempts += 1
        
        print(f"[DEBUG] No more players need to act, checking if betting round is complete")
        
        # 检查是否只剩一个活跃玩家，如果是则直接进入摊牌
        active_players = [p for p in self.players if p.is_active and not p.is_folded]
        if len(active_players) <= 1:
            print(f"[DEBUG] Only {len(active_players)} active players left, going to showdown")
            self.game_stage = "showdown"
            self._showdown()
            return
        
        # 特殊处理两人游戏preflop阶段：如果小盲注跟注了，需要给大盲注一个行动机会
        if len(self.players) == 2 and self.game_stage == "preflop":
            players_acted = [p for p in active_players if p.has_acted_this_round]
            all_bets_equal = all(p.current_bet == self.current_bet or p.is_all_in for p in active_players)
            
            # 如果只有小盲注行动过且下注相等（小盲跟注），设置大盲注为当前玩家
            if len(players_acted) == 1 and all_bets_equal:
                # 找到大盲注玩家（非庄家位置）
                for i, player in enumerate(self.players):
                    if player.position != self.dealer_position and player.is_active and not player.is_folded:
                        self.current_player_index = i
                        print(f"[DEBUG] Two-player preflop: Setting big blind as current player: {player.user_id} at index {i}")
                        return
        
        # 如果没有找到需要行动的玩家，检查下注轮是否完成
        if self._is_betting_round_complete():
            print(f"[DEBUG] Betting round complete, moving to next stage")
            self._next_stage()
        else:
            # 如果下注轮未完成但没有玩家需要行动，可能是逻辑错误
            print(f"[DEBUG] Warning: No players need to act but betting round not complete")
            # 设置为第一个活跃且未弃牌的玩家
            for i, player in enumerate(self.players):
                if player.is_active and not player.is_folded:
                    self.current_player_index = i
                    print(f"[DEBUG] Reset to first active player: {player.user_id} at index {i}")
                    break
    
    def _is_betting_round_complete(self) -> bool:
        """检查下注轮是否完成"""
        active_players = [p for p in self.players if p.is_active and not p.is_folded]
        
        print(f"[DEBUG] _is_betting_round_complete: active_players count = {len(active_players)}")
        print(f"[DEBUG] Active players: {[(p.user_id, p.current_bet, p.is_all_in, p.has_acted_this_round) for p in active_players]}")
        print(f"[DEBUG] Current bet: {self.current_bet}")
        print(f"[DEBUG] Game stage: {self.game_stage}")
        
        if len(active_players) <= 1:
            print(f"[DEBUG] Betting round complete: only {len(active_players)} active players")
            return True
        
        # 检查是否所有活跃玩家都all-in，如果是则直接进入结算
        all_players_all_in = all(p.is_all_in for p in active_players)
        if all_players_all_in:
            print(f"[DEBUG] Betting round complete: all active players are all-in")
            return True
        
        # 特殊处理两人游戏preflop阶段                                                                                                                      
        if len(active_players) == 2 and self.game_stage == "preflop":
            # 在两人游戏preflop阶段，小盲注先行动，然后大盲注有机会行动
            players_acted = [p for p in active_players if p.has_acted_this_round]
            print(f"[DEBUG] Preflop two-player: {len(players_acted)} players have acted")
            
            # 检查是否所有玩家的下注都相等
            all_bets_equal = all(p.current_bet == self.current_bet or p.is_all_in for p in active_players)
            all_have_acted = all(p.has_acted_this_round for p in active_players)
            print(f"[DEBUG] Preflop: all_bets_equal={all_bets_equal}, all_have_acted={all_have_acted}")
            
            # 两人游戏preflop规则：
            # 1. 如果小盲注还没行动，轮次未完成
            # 2. 如果小盲注行动了但大盲注还没行动，且下注不相等（小盲加注），轮次未完成
            # 3. 如果小盲注行动了且下注相等（小盲跟注），给大盲注一个行动机会
            # 4. 只有当大盲注也行动过，或者所有下注相等且至少小盲注行动过，轮次才完成
            
            if len(players_acted) == 0:
                print(f"[DEBUG] Preflop: No players have acted yet, round not complete")
                return False
            
            # 如果所有玩家都行动过且下注相等，轮次完成
            if all_have_acted and all_bets_equal:
                print(f"[DEBUG] Preflop: All players have acted and bets are equal, round complete")
                return True
            
            # 如果只有小盲注行动过，且下注相等（小盲跟注），给大盲注一个check的机会
            if len(players_acted) == 1 and all_bets_equal:
                print(f"[DEBUG] Preflop: Small blind called, big blind gets a chance to act")
                return False
            
            print(f"[DEBUG] Preflop: Round not complete - players_acted={len(players_acted)}, all_bets_equal={all_bets_equal}, all_have_acted={all_have_acted}")
            return False
        
        # 常规逻辑：检查所有活跃玩家是否都已行动且下注相等
        players_need_action = []
        for player in active_players:
            if not player.is_all_in and player.current_bet < self.current_bet:
                players_need_action.append(player.user_id)
        
        if players_need_action:
            print(f"[DEBUG] Betting round NOT complete: players {players_need_action} still need to act")
            return False
        
        # 确保所有玩家都已在本轮行动过（除了all_in的玩家）
        players_not_acted = [p.user_id for p in active_players if not p.has_acted_this_round and not p.is_all_in]
        if players_not_acted:
            print(f"[DEBUG] Betting round NOT complete: players {players_not_acted} haven't acted this round")
            return False
        
        # 检查是否所有玩家的下注都相等（或者是all_in）
        all_bets_equal = all(p.current_bet == self.current_bet or p.is_all_in for p in active_players)
        if not all_bets_equal:
            print(f"[DEBUG] Betting round NOT complete: bets are not equal")
            return False
        
        # 特殊情况：如果所有玩家都已行动且下注都为0（所有人都check），轮次完成
        if self.current_bet == 0 and all(p.has_acted_this_round or p.is_all_in for p in active_players):
            print(f"[DEBUG] Betting round complete: all players checked (current_bet=0)")
            return True
        
        print(f"[DEBUG] Betting round complete: all players have acted and bets are equal")
        return True
    
    def _next_stage(self):
        """进入下一阶段"""
        # 检查是否只剩一个活跃玩家，如果是则直接进入摊牌
        active_players = [p for p in self.players if p.is_active and not p.is_folded]
        if len(active_players) <= 1:
            print(f"[DEBUG] Only {len(active_players)} active players left, going to showdown")
            self.game_stage = "showdown"
            self._showdown()
            return
        
        # 检查是否所有活跃玩家都all-in，如果是则直接进入摊牌
        all_players_all_in = all(p.is_all_in for p in active_players)
        if all_players_all_in:
            print(f"[DEBUG] All active players are all-in, going directly to showdown")
            # 如果还没有发完所有公共牌，需要先发完
            if self.game_stage == "preflop":
                # 发翻牌、转牌、河牌
                self.community_cards.extend(self.deck.deal_cards(5))
                print(f"[DEBUG] Dealt all remaining community cards for all-in showdown")
            elif self.game_stage == "flop":
                # 发转牌、河牌
                self.community_cards.extend(self.deck.deal_cards(2))
                print(f"[DEBUG] Dealt turn and river for all-in showdown")
            elif self.game_stage == "turn":
                # 发河牌
                self.community_cards.extend(self.deck.deal_cards(1))
                print(f"[DEBUG] Dealt river for all-in showdown")
            
            self.game_stage = "showdown"
            self._showdown()
            return
        
        # 重置玩家当前下注
        for player in self.players:
            player.reset_for_new_round()
        
        self.current_bet = 0
        
        if self.game_stage == "preflop":
            # 发翻牌
            self.community_cards.extend(self.deck.deal_cards(3))
            self.game_stage = "flop"
        elif self.game_stage == "flop":
            # 发转牌
            self.community_cards.extend(self.deck.deal_cards(1))
            self.game_stage = "turn"
        elif self.game_stage == "turn":
            # 发河牌
            self.community_cards.extend(self.deck.deal_cards(1))
            self.game_stage = "river"
        elif self.game_stage == "river":
            # 摊牌
            print(f"[DEBUG] River stage complete, going to showdown")
            self.game_stage = "showdown"
            self._showdown()
            # 游戏结束后设置为finished状态
            self.game_stage = "finished"
            print(f"[DEBUG] Game finished, stage set to: {self.game_stage}")
            return
        
        # 设置下一轮的第一个行动玩家（小盲注位置）
        # 找到庄家在数组中的索引
        dealer_array_index = None
        for i, player in enumerate(self.players):
            if player.position == self.dealer_position:
                dealer_array_index = i
                break
        
        if dealer_array_index is not None:
            if len(self.players) == 2:
                # 两人游戏：小盲注位置（庄家）先行动
                self.current_player_index = dealer_array_index
            else:
                # 多人游戏：小盲注位置（庄家后第1个玩家）
                self.current_player_index = (dealer_array_index + 1) % len(self.players)
        else:
            # 如果找不到庄家，默认从第一个玩家开始
            self.current_player_index = 0
        
        self._find_next_active_player()
    
    def _find_next_active_player(self):
        """找到下一个活跃玩家"""
        start_index = self.current_player_index
        attempts = 0
        max_attempts = len(self.players)
        
        while attempts < max_attempts:
            current_player = self.players[self.current_player_index]
            print(f"[DEBUG] _find_next_active_player: checking player {current_player.user_id} at index {self.current_player_index}")
            print(f"[DEBUG] Player state: is_active={current_player.is_active}, is_folded={current_player.is_folded}, is_all_in={current_player.is_all_in}")
            
            # 找到活跃且未弃牌的玩家（all_in玩家也可以是当前玩家）
            if current_player.is_active and not current_player.is_folded:
                print(f"[DEBUG] Found active player: {current_player.user_id} at index {self.current_player_index}")
                return
            
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            attempts += 1
        
        # 如果没有找到活跃玩家，直接到摊牌
        print(f"[DEBUG] No active players found, going to showdown")
        self.game_stage = "showdown"
        self._showdown()
        # 确保游戏状态设置为finished
        if not self.game_stage == "finished":
            self.game_stage = "finished"
            print(f"[DEBUG] Game stage set to finished after showdown")
    
    def _showdown(self):
        """摊牌阶段"""
        print(f"[DEBUG] _showdown called")
        active_players = [p for p in self.players if not p.is_folded]
        print(f"[DEBUG] Active players in showdown: {[p.user_id for p in active_players]}")
        
        if len(active_players) == 1:
            # 只有一个玩家，直接获胜
            winner = active_players[0]
            winner.chips += self.pot
            print(f"[DEBUG] Single winner: {winner.user_id}, won {self.pot} chips")
            self.is_finished = True
            self.game_stage = "finished"
            # 生成游戏结果数据
            self.game_results = self._generate_game_results(active_players, winner, self.pot)
            # 更新庄家位置到下一个玩家
            self._move_dealer_position()
            # 注意：不再立即重置玩家状态，由websocket_handler延迟处理
            return
        
        # 评估所有玩家的手牌
        player_hands = []
        for player in active_players:
            all_cards = player.hole_cards + self.community_cards
            hand_rank, hand_values = HandEvaluator.evaluate_hand(all_cards)
            player_hands.append((player, hand_rank, hand_values))
            print(f"[DEBUG] Player {player.user_id} hand: {hand_rank}, values: {hand_values}")
        
        # 按手牌强度排序
        player_hands.sort(key=lambda x: (x[1].value, x[2]), reverse=True)
        
        # 分配奖池
        winner = player_hands[0][0]
        winner.chips += self.pot
        print(f"[DEBUG] Showdown winner: {winner.user_id}, won {self.pot} chips")
        
        self.is_finished = True
        self.game_stage = "finished"
        # 生成游戏结果数据
        self.game_results = self._generate_game_results(active_players, winner, self.pot, player_hands)
        # 更新庄家位置到下一个玩家
        self._move_dealer_position()
        # 注意：不再立即重置玩家状态，由websocket_handler延迟处理
    
    def _generate_game_results(self, active_players: List[Player], winner: Player, pot_amount: int, player_hands: List = None) -> Dict:
        """生成游戏结果数据"""
        results = []
        
        if player_hands:
            # 多人摊牌情况
            for i, (player, hand_rank, hand_values) in enumerate(player_hands):
                win_amount = pot_amount if player == winner else 0
                results.append({
                    'user_id': player.user_id,
                    'username': player.username,
                    'hole_cards': [card.to_dict() for card in player.hole_cards],
                    'hand_rank': hand_rank.name,
                    'hand_rank_value': hand_rank.value,
                    'hand_strength': hand_values,
                    'win_amount': win_amount,
                    'final_chips': player.chips,
                    'rank': i + 1
                })
        else:
            # 单人获胜情况
            for player in active_players:
                win_amount = pot_amount if player == winner else 0
                all_cards = player.hole_cards + self.community_cards
                hand_rank, hand_values = HandEvaluator.evaluate_hand(all_cards)
                results.append({
                    'user_id': player.user_id,
                    'username': player.username,
                    'hole_cards': [card.to_dict() for card in player.hole_cards],
                    'hand_rank': hand_rank.name,
                    'hand_rank_value': hand_rank.value,
                    'hand_strength': hand_values,
                    'win_amount': win_amount,
                    'final_chips': player.chips,
                    'rank': 1 if player == winner else 2
                })
        
        return {
            'pot_amount': pot_amount,
            'winner_id': winner.user_id,
            'results': results
        }
    
    def get_hand_rank_name(self, hand_rank: HandRank) -> str:
        """获取手牌类型的中文名称"""
        rank_names = {
            HandRank.HIGH_CARD: "高牌",
            HandRank.PAIR: "一对",
            HandRank.TWO_PAIR: "两对",
            HandRank.THREE_OF_A_KIND: "三条",
            HandRank.STRAIGHT: "顺子",
            HandRank.FLUSH: "同花",
            HandRank.FULL_HOUSE: "葫芦",
            HandRank.FOUR_OF_A_KIND: "四条",
            HandRank.STRAIGHT_FLUSH: "同花顺",
            HandRank.ROYAL_FLUSH: "皇家同花顺"
        }
        return rank_names.get(hand_rank, "未知")
    
    def _move_dealer_position(self):
        """将庄家位置移动到下一个玩家（顺时针）"""
        if len(self.players) < 2:
            return
        
        # 找到当前庄家在数组中的索引
        current_dealer_index = None
        for i, player in enumerate(self.players):
            if player.position == self.dealer_position:
                current_dealer_index = i
                break
        
        if current_dealer_index is not None:
            # 移动到下一个玩家（顺时针）
            next_dealer_index = (current_dealer_index + 1) % len(self.players)
            self.dealer_position = self.players[next_dealer_index].position
            print(f"[DEBUG] Dealer position moved from {self.players[current_dealer_index].position} to {self.dealer_position}")
        else:
            # 如果找不到当前庄家，设置为第一个玩家
            if self.players:
                self.dealer_position = self.players[0].position
                print(f"[DEBUG] Dealer position reset to {self.dealer_position}")
    
    def _reset_all_players_ready_status(self):
        """将所有玩家的准备状态设为未准备，并清空游戏状态"""
        for player in self.players:
            player.is_ready = False
            # 清空玩家状态但保留余额
            player.hole_cards = []
            player.current_bet = 0
            player.total_bet = 0
            player.is_folded = False
            player.is_all_in = False
            player.is_active = True
            player.has_acted_this_round = False
        
        # 重置游戏状态为等待
        self.game_stage = "waiting"
        self.is_finished = False
        self.pot = 0
        self.current_bet = 0
        self.current_player_index = 0
        self.community_cards = []
        self.game_results = None
        
        print(f"[DEBUG] All players ready status reset to False and game state cleared")
    
    def set_player_ready(self, user_id: int, ready: bool) -> bool:
        """设置玩家准备状态"""
        player = self._get_player_by_id(user_id)
        if not player:
            return False
        
        player.is_ready = ready
        return True
    
    def change_player_seat(self, user_id: int, new_position: int) -> bool:
        """切换玩家座位"""
        print(f"[DEBUG] change_player_seat called: user_id={user_id}, new_position={new_position}")
        
        if self.game_stage != "waiting":
            print(f"[DEBUG] Cannot change seat during game stage: {self.game_stage}")
            return False  # 游戏进行中不能切换座位
        
        player = self._get_player_by_id(user_id)
        if not player:
            print(f"[DEBUG] Player with user_id {user_id} not found in game")
            return False
        
        # 检查新位置是否有效（支持9个座位：0-8）
        if new_position < 0 or new_position >= 9:
            print(f"[DEBUG] Invalid position: {new_position} (must be 0-8)")
            return False
        
        print(f"[DEBUG] Checking if position {new_position} is occupied...")
        # 检查新位置是否被占用
        for p in self.players:
            if p.position == new_position and p.user_id != user_id:
                print(f"[DEBUG] Position {new_position} is already occupied by user {p.user_id}")
                return False
        
        print(f"[DEBUG] Position {new_position} is available")
        
        # 更新玩家位置
        old_position = player.position
        player.position = new_position
        print(f"[DEBUG] Player {user_id} moved from position {old_position} to {new_position}")
        
        # 重新排序玩家列表，确保按座位位置排序
        self.players.sort(key=lambda p: (p.position if p.position >= 0 else 999, p.user_id))
        print(f"[DEBUG] Players after sorting: {[(p.user_id, p.position) for p in self.players]}")
        
        return True
    
    def get_game_state(self, user_id: Optional[int] = None) -> Dict:
        """获取游戏状态"""
        print(f"[DEBUG] get_game_state called for user {user_id}")
        print(f"[DEBUG] Current players in game: {[(p.user_id, p.position) for p in self.players]}")
        print(f"[DEBUG] Game stage: {self.game_stage}, current_player_index: {self.current_player_index}")
        
        players_data = []
        for player in self.players:
            player_dict = player.to_dict(show_hole_cards=(user_id == player.user_id))
            players_data.append(player_dict)
            print(f"[DEBUG] Player data: user_id={player.user_id}, position={player.position}, dict_position={player_dict.get('position')}")
        
        # 确定当前行动玩家
        current_player = None
        if self.game_stage != "waiting" and self.game_stage != "finished" and self.game_stage != "showdown":
            if 0 <= self.current_player_index < len(self.players):
                current_player = self.players[self.current_player_index].user_id
                print(f"[DEBUG] Current player determined: {current_player} at index {self.current_player_index}")
            else:
                print(f"[DEBUG] Invalid current_player_index: {self.current_player_index}, players count: {len(self.players)}")
        else:
            print(f"[DEBUG] Game stage {self.game_stage} - no current player needed")
        
        state = {
            "room_id": self.room_id,
            "stage": self.game_stage,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "current_player": current_player,
            "community_cards": [card.to_dict() for card in self.community_cards],
            "players": players_data,
            "is_finished": self.is_finished
        }
        
        print(f"[DEBUG] Final game state players: {[(p['user_id'], p['position']) for p in state['players']]}")
        print(f"[DEBUG] Game stage: {self.game_stage}, current_player_index: {self.current_player_index}")
        print(f"[DEBUG] Current player: {state['current_player']}, dealer_position: {self.dealer_position}")
        print(f"[DEBUG] Pot: {self.pot}, current_bet: {self.current_bet}")
        return state

class PokerGameManager:
    def __init__(self):
        self.games: Dict[int, PokerGame] = {}
    
    def create_game(self, room_id: int, small_blind: int, big_blind: int) -> PokerGame:
        """创建新游戏"""
        game = PokerGame(room_id, small_blind, big_blind)
        self.games[room_id] = game
        return game
    
    def get_game(self, room_id: int) -> Optional[PokerGame]:
        """获取游戏"""
        return self.games.get(room_id)
    
    def remove_game(self, room_id: int):
        """移除游戏"""
        if room_id in self.games:
            del self.games[room_id]