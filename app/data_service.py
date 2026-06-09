"""
数据服务层 - 实现所有新功能的数据模型和存储
包括：Badcase管理、模型调用记录、调用链路追踪、积分体系、分享打卡、积分商城等
"""

import json
import os
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def _load_json(filepath: str, default: Any = None) -> Any:
    if not os.path.exists(filepath):
        return default if default is not None else []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default if default is not None else []

def _save_json(filepath: str, data: Any):
    _ensure_dir(os.path.dirname(filepath))
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============================================================
# 1. Badcase 管理
# ============================================================
BADCASE_FILE = os.path.join(DATA_DIR, "badcases.json")

class BadcaseService:
    def __init__(self):
        self.badcases = _load_json(BADCASE_FILE, [])
    
    def _save(self):
        _save_json(BADCASE_FILE, self.badcases)
    
    def list_badcases(self, status: str = None, category: str = None, limit: int = 100) -> List[Dict]:
        result = self.badcases
        if status:
            result = [b for b in result if b.get('status') == status]
        if category:
            result = [b for b in result if b.get('category') == category]
        return sorted(result, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
    
    def create_badcase(self, session_id: str, category: str, description: str, 
                       severity: str = 'medium', assigned_to: str = '', 
                       conversation_snippet: str = '') -> Dict:
        badcase = {
            'id': f"bc_{uuid.uuid4().hex[:8]}",
            'session_id': session_id,
            'category': category,
            'description': description,
            'severity': severity,
            'status': 'open',
            'assigned_to': assigned_to,
            'conversation_snippet': conversation_snippet,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'resolution': '',
            'resolution_time': None
        }
        self.badcases.append(badcase)
        self._save()
        return badcase
    
    def update_badcase(self, badcase_id: str, updates: Dict) -> Optional[Dict]:
        for b in self.badcases:
            if b['id'] == badcase_id:
                b.update(updates)
                b['updated_at'] = datetime.now().isoformat()
                if updates.get('status') == 'resolved' and not b.get('resolution_time'):
                    b['resolution_time'] = datetime.now().isoformat()
                self._save()
                return b
        return None
    
    def get_stats(self) -> Dict:
        total = len(self.badcases)
        open_count = sum(1 for b in self.badcases if b.get('status') == 'open')
        resolved = sum(1 for b in self.badcases if b.get('status') == 'resolved')
        categories = {}
        for b in self.badcases:
            cat = b.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        return {
            'total': total,
            'open': open_count,
            'resolved': resolved,
            'categories': categories
        }

# ============================================================
# 2. 模型调用记录与Token统计
# ============================================================
MODEL_CALLS_FILE = os.path.join(DATA_DIR, "model_calls.json")

class ModelCallService:
    def __init__(self):
        self.calls = _load_json(MODEL_CALLS_FILE, [])
    
    def _save(self):
        _save_json(MODEL_CALLS_FILE, self.calls)
    
    def record_call(self, session_id: str, conversation_id: str, model_name: str,
                    prompt_tokens: int, completion_tokens: int, total_tokens: int,
                    response_time_ms: int, module_type: str, status: str = 'success',
                    error_message: str = '', cost_usd: float = 0.0) -> Dict:
        call = {
            'call_id': f"call_{uuid.uuid4().hex[:12]}",
            'session_id': session_id,
            'conversation_id': conversation_id,
            'model_name': model_name,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'response_time_ms': response_time_ms,
            'module_type': module_type,
            'status': status,
            'error_message': error_message,
            'cost_usd': cost_usd,
            'created_at': datetime.now().isoformat()
        }
        self.calls.append(call)
        self._save()
        return call
    
    def list_calls(self, model_name: str = None, module_type: str = None, 
                   status: str = None, limit: int = 100) -> List[Dict]:
        result = self.calls
        if model_name:
            result = [c for c in result if c.get('model_name') == model_name]
        if module_type:
            result = [c for c in result if c.get('module_type') == module_type]
        if status:
            result = [c for c in result if c.get('status') == status]
        return sorted(result, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
    
    def get_stats(self, days: int = 7) -> Dict:
        cutoff = datetime.now() - timedelta(days=days)
        recent = [c for c in self.calls if datetime.fromisoformat(c['created_at']) > cutoff]
        
        total_calls = len(recent)
        total_tokens = sum(c.get('total_tokens', 0) for c in recent)
        total_cost = sum(c.get('cost_usd', 0) for c in recent)
        avg_time = sum(c.get('response_time_ms', 0) for c in recent) / total_calls if total_calls > 0 else 0
        success_count = sum(1 for c in recent if c.get('status') == 'success')
        
        # 按模块统计
        module_stats = {}
        for c in recent:
            mod = c.get('module_type', 'unknown')
            if mod not in module_stats:
                module_stats[mod] = {'calls': 0, 'tokens': 0}
            module_stats[mod]['calls'] += 1
            module_stats[mod]['tokens'] += c.get('total_tokens', 0)
        
        # 按天统计
        daily = {}
        for c in recent:
            day = c['created_at'][:10]
            if day not in daily:
                daily[day] = {'tokens': 0, 'calls': 0, 'cost': 0}
            daily[day]['tokens'] += c.get('total_tokens', 0)
            daily[day]['calls'] += 1
            daily[day]['cost'] += c.get('cost_usd', 0)
        
        return {
            'total_calls': total_calls,
            'total_tokens': total_tokens,
            'total_cost_usd': round(total_cost, 4),
            'avg_response_time_ms': round(avg_time, 2),
            'success_rate': round(success_count / total_calls * 100, 2) if total_calls > 0 else 0,
            'module_stats': module_stats,
            'daily_stats': daily
        }

# ============================================================
# 3. 调用链路追踪
# ============================================================
TRACE_FILE = os.path.join(DATA_DIR, "traces.json")

class TraceService:
    def __init__(self):
        self.traces = _load_json(TRACE_FILE, [])
    
    def _save(self):
        _save_json(TRACE_FILE, self.traces)
    
    def create_trace(self, session_id: str, user_message: str) -> str:
        trace_id = f"txh_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"
        trace = {
            'trace_id': trace_id,
            'session_id': session_id,
            'user_message': user_message,
            'status': 'running',
            'total_duration_ms': 0,
            'nodes': [],
            'created_at': datetime.now().isoformat(),
            'completed_at': None
        }
        self.traces.append(trace)
        self._save()
        return trace_id
    
    def add_node(self, trace_id: str, node_type: str, input_data: Dict, 
                 output_data: Dict, duration_ms: int, status: str = 'success',
                 error_message: str = '') -> bool:
        for trace in self.traces:
            if trace['trace_id'] == trace_id:
                node = {
                    'node_id': f"{trace_id}_node_{len(trace['nodes'])}",
                    'node_type': node_type,
                    'input_data': input_data,
                    'output_data': output_data,
                    'duration_ms': duration_ms,
                    'status': status,
                    'error_message': error_message,
                    'created_at': datetime.now().isoformat()
                }
                trace['nodes'].append(node)
                trace['total_duration_ms'] = sum(n.get('duration_ms', 0) for n in trace['nodes'])
                self._save()
                return True
        return False
    
    def complete_trace(self, trace_id: str, status: str = 'success'):
        for trace in self.traces:
            if trace['trace_id'] == trace_id:
                trace['status'] = status
                trace['completed_at'] = datetime.now().isoformat()
                self._save()
                return True
        return False
    
    def get_trace(self, trace_id: str) -> Optional[Dict]:
        for trace in self.traces:
            if trace['trace_id'] == trace_id:
                return trace
        return None
    
    def list_traces(self, session_id: str = None, limit: int = 50) -> List[Dict]:
        result = self.traces
        if session_id:
            result = [t for t in result if t.get('session_id') == session_id]
        return sorted(result, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]

# ============================================================
# 4. 用户积分体系
# ============================================================
POINTS_FILE = os.path.join(DATA_DIR, "user_points.json")
POINT_TRANSACTIONS_FILE = os.path.join(DATA_DIR, "point_transactions.json")

class PointsService:
    def __init__(self):
        self.accounts = _load_json(POINTS_FILE, {})
        self.transactions = _load_json(POINT_TRANSACTIONS_FILE, [])
        self._init_config()
    
    def _init_config(self):
        self.config = _load_json(os.path.join(DATA_DIR, "points_config.json"), {
            'initial_points': 100,
            'dialogue_points': 5,
            'dialogue_daily_limit': 50,
            'share_points': 20,
            'share_daily_limit': 100,
            'checkin_points': 10,
            'checkin_3day_bonus': 20,
            'checkin_7day_bonus': 50,
            'checkin_30day_bonus': 200,
            'enable_dialogue': True,
            'enable_share': True,
            'enable_checkin': True
        })
    
    def _save_accounts(self):
        _save_json(POINTS_FILE, self.accounts)
    
    def _save_transactions(self):
        _save_json(POINT_TRANSACTIONS_FILE, self.transactions)
    
    def _save_config(self):
        _save_json(os.path.join(DATA_DIR, "points_config.json"), self.config)
    
    def get_or_create_account(self, session_id: str) -> Dict:
        if session_id not in self.accounts:
            self.accounts[session_id] = {
                'session_id': session_id,
                'total_points': self.config['initial_points'],
                'available_points': self.config['initial_points'],
                'consumed_points': 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            # 记录初始积分流水
            self._add_transaction(session_id, 'earn', 'initial', self.config['initial_points'], 
                                  self.config['initial_points'], '新用户初始积分')
            self._save_accounts()
        return self.accounts[session_id]
    
    def _add_transaction(self, session_id: str, transaction_type: str, source: str,
                         points: int, balance_after: int, description: str):
        txn = {
            'id': f"txn_{uuid.uuid4().hex[:8]}",
            'session_id': session_id,
            'transaction_type': transaction_type,
            'source': source,
            'points': points,
            'balance_after': balance_after,
            'description': description,
            'created_at': datetime.now().isoformat()
        }
        self.transactions.append(txn)
        self._save_transactions()
        return txn
    
    def earn_points(self, session_id: str, source: str, points: int, description: str) -> Dict:
        account = self.get_or_create_account(session_id)
        account['total_points'] += points
        account['available_points'] += points
        account['updated_at'] = datetime.now().isoformat()
        self._save_accounts()
        txn = self._add_transaction(session_id, 'earn', source, points, 
                                     account['available_points'], description)
        return {'success': True, 'account': account, 'transaction': txn}
    
    def consume_points(self, session_id: str, points: int, description: str) -> Dict:
        account = self.get_or_create_account(session_id)
        if account['available_points'] < points:
            return {'success': False, 'error': '积分不足'}
        account['available_points'] -= points
        account['consumed_points'] += points
        account['updated_at'] = datetime.now().isoformat()
        self._save_accounts()
        txn = self._add_transaction(session_id, 'consume', 'shop', -points, 
                                     account['available_points'], description)
        return {'success': True, 'account': account, 'transaction': txn}
    
    def get_balance(self, session_id: str) -> Dict:
        account = self.get_or_create_account(session_id)
        return {'success': True, 'account': account}
    
    def get_transactions(self, session_id: str, limit: int = 50) -> List[Dict]:
        result = [t for t in self.transactions if t.get('session_id') == session_id]
        return sorted(result, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
    
    def get_config(self) -> Dict:
        return self.config
    
    def update_config(self, updates: Dict) -> Dict:
        self.config.update(updates)
        self._save_config()
        return self.config

# ============================================================
# 5. 分享与打卡
# ============================================================
CHECKIN_FILE = os.path.join(DATA_DIR, "checkin_records.json")
SHARE_FILE = os.path.join(DATA_DIR, "share_records.json")

class CheckinService:
    def __init__(self, points_service: PointsService):
        self.records = _load_json(CHECKIN_FILE, [])
        self.points = points_service
    
    def _save(self):
        _save_json(CHECKIN_FILE, self.records)
    
    def checkin(self, session_id: str) -> Dict:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 检查今日是否已打卡
        for r in self.records:
            if r.get('session_id') == session_id and r.get('checkin_date') == today:
                return {'success': False, 'error': '今日已打卡'}
        
        # 计算连续天数
        consecutive = self._get_consecutive_days(session_id)
        
        # 计算积分
        config = self.points.get_config()
        points_earned = config.get('checkin_points', 10)
        bonus = 0
        if consecutive >= 30:
            bonus = config.get('checkin_30day_bonus', 200)
        elif consecutive >= 7:
            bonus = config.get('checkin_7day_bonus', 50)
        elif consecutive >= 3:
            bonus = config.get('checkin_3day_bonus', 20)
        
        total_points = points_earned + bonus
        
        record = {
            'id': f"ck_{uuid.uuid4().hex[:8]}",
            'session_id': session_id,
            'checkin_date': today,
            'consecutive_days': consecutive + 1,
            'points_earned': total_points,
            'bonus': bonus,
            'created_at': datetime.now().isoformat()
        }
        self.records.append(record)
        self._save()
        
        # 发放积分
        desc = f'每日打卡 +{points_earned}分'
        if bonus > 0:
            desc += f'，连续{consecutive + 1}天奖励 +{bonus}分'
        self.points.earn_points(session_id, 'checkin', total_points, desc)
        
        return {'success': True, 'record': record, 'consecutive_days': consecutive + 1}
    
    def _get_consecutive_days(self, session_id: str) -> int:
        user_records = [r for r in self.records if r.get('session_id') == session_id]
        if not user_records:
            return 0
        
        user_records.sort(key=lambda x: x.get('checkin_date', ''), reverse=True)
        consecutive = 0
        today = datetime.now().date()
        
        for r in user_records:
            checkin_date = datetime.strptime(r['checkin_date'], '%Y-%m-%d').date()
            expected_date = today - timedelta(days=consecutive)
            if checkin_date == expected_date:
                consecutive += 1
            else:
                break
        return consecutive
    
    def get_status(self, session_id: str) -> Dict:
        today = datetime.now().strftime('%Y-%m-%d')
        checked_today = any(r.get('session_id') == session_id and r.get('checkin_date') == today 
                           for r in self.records)
        consecutive = self._get_consecutive_days(session_id)
        
        # 获取本月打卡记录
        current_month = datetime.now().strftime('%Y-%m')
        month_records = [r for r in self.records 
                        if r.get('session_id') == session_id and r.get('checkin_date', '').startswith(current_month)]
        
        return {
            'success': True,
            'checked_today': checked_today,
            'consecutive_days': consecutive,
            'month_records': month_records
        }

class ShareService:
    def __init__(self, points_service: PointsService):
        self.records = _load_json(SHARE_FILE, [])
        self.points = points_service
    
    def _save(self):
        _save_json(SHARE_FILE, self.records)
    
    def create_share(self, sharer_session_id: str) -> Dict:
        share_code = f"share_{uuid.uuid4().hex[:8]}"
        record = {
            'id': f"shr_{uuid.uuid4().hex[:8]}",
            'sharer_session_id': sharer_session_id,
            'share_code': share_code,
            'visitor_session_id': None,
            'points_given': False,
            'created_at': datetime.now().isoformat()
        }
        self.records.append(record)
        self._save()
        return {'success': True, 'share_code': share_code}
    
    def verify_share(self, share_code: str, visitor_session_id: str) -> Dict:
        # 查找分享记录
        record = None
        for r in self.records:
            if r.get('share_code') == share_code:
                record = r
                break
        
        if not record:
            return {'success': False, 'error': '无效的分享码'}
        
        if record.get('visitor_session_id'):
            return {'success': False, 'error': '该分享码已被使用'}
        
        if record['sharer_session_id'] == visitor_session_id:
            return {'success': False, 'error': '不能使用自己的分享码'}
        
        config = self.points.get_config()
        
        # 检查分享者今日上限
        today = datetime.now().strftime('%Y-%m-%d')
        sharer_today = sum(1 for r in self.records 
                          if r.get('sharer_session_id') == record['sharer_session_id'] 
                          and r.get('created_at', '').startswith(today) and r.get('points_given'))
        
        if sharer_today >= config.get('share_daily_limit', 100) / max(config.get('share_points', 20), 1):
            return {'success': False, 'error': '分享者今日已达上限'}
        
        # 更新记录
        record['visitor_session_id'] = visitor_session_id
        record['points_given'] = True
        self._save()
        
        # 给分享者发积分
        sharer_points = config.get('share_points', 20)
        self.points.earn_points(record['sharer_session_id'], 'share', sharer_points, 
                                f'分享推广 +{sharer_points}分')
        
        # 给被分享者发积分（首次）
        visitor_points = 50
        self.points.earn_points(visitor_session_id, 'share', visitor_points, 
                                f'好友分享奖励 +{visitor_points}分')
        
        return {'success': True, 'sharer_points': sharer_points, 'visitor_points': visitor_points}

# ============================================================
# 6. 积分等级体系
# ============================================================
LEVELS = [
    {'level': 1, 'title': '健康新手', 'icon': '🌱', 'min_points': 0, 'max_points': 99},
    {'level': 2, 'title': '健康学徒', 'icon': '🌿', 'min_points': 100, 'max_points': 299},
    {'level': 3, 'title': '健康达人', 'icon': '🍀', 'min_points': 300, 'max_points': 599},
    {'level': 4, 'title': '健康专家', 'icon': '🌸', 'min_points': 600, 'max_points': 999},
    {'level': 5, 'title': '健康之星', 'icon': '⭐', 'min_points': 1000, 'max_points': 1499},
    {'level': 6, 'title': '健康导师', 'icon': '🌟', 'min_points': 1500, 'max_points': 2199},
    {'level': 7, 'title': '健康大师', 'icon': '💎', 'min_points': 2200, 'max_points': 2999},
    {'level': 8, 'title': '健康王者', 'icon': '👑', 'min_points': 3000, 'max_points': 4999},
    {'level': 9, 'title': '健康传奇', 'icon': '🏆', 'min_points': 5000, 'max_points': 9999},
    {'level': 10, 'title': '健康神话', 'icon': '🦄', 'min_points': 10000, 'max_points': 999999}
]

class LevelService:
    def __init__(self, points_service: PointsService):
        self.points = points_service
    
    def get_level(self, total_points: int) -> Dict:
        for level in LEVELS:
            if level['min_points'] <= total_points <= level['max_points']:
                return level
        return LEVELS[-1]
    
    def get_user_level(self, session_id: str) -> Dict:
        account = self.points.get_or_create_account(session_id)
        total_points = account.get('total_points', 0)
        level = self.get_level(total_points)
        
        # 计算进度
        next_level = None
        for l in LEVELS:
            if l['level'] == level['level'] + 1:
                next_level = l
                break
        
        progress = 100
        if next_level:
            progress = min(100, int((total_points - level['min_points']) / 
                           (next_level['min_points'] - level['min_points']) * 100))
        
        return {
            'success': True,
            'level': level,
            'total_points': total_points,
            'progress': progress,
            'next_level': next_level
        }
    
    def get_all_levels(self) -> List[Dict]:
        return LEVELS

# ============================================================
# 7. 积分商城
# ============================================================
SHOP_PRODUCTS_FILE = os.path.join(DATA_DIR, "shop_products.json")
EXCHANGE_RECORDS_FILE = os.path.join(DATA_DIR, "exchange_records.json")

class ShopService:
    def __init__(self, points_service: PointsService):
        self.products = _load_json(SHOP_PRODUCTS_FILE, [])
        self.exchanges = _load_json(EXCHANGE_RECORDS_FILE, [])
        self.points = points_service
        self._init_default_products()
    
    def _init_default_products(self):
        if not self.products:
            self.products = [
                {
                    'id': 'prod_001',
                    'name': '专属主题皮肤',
                    'description': '解锁泰小虎专属主题皮肤',
                    'type': 'virtual',
                    'points_cost': 200,
                    'stock': -1,
                    'limit_per_user': 1,
                    'status': 'active',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 'prod_002',
                    'name': '8折优惠券',
                    'description': '购买产品享受8折优惠',
                    'type': 'coupon',
                    'points_cost': 500,
                    'stock': 100,
                    'limit_per_user': 5,
                    'status': 'active',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 'prod_003',
                    'name': '深度健康报告',
                    'description': '生成个性化深度健康分析报告',
                    'type': 'virtual',
                    'points_cost': 300,
                    'stock': -1,
                    'limit_per_user': 1,
                    'status': 'active',
                    'created_at': datetime.now().isoformat()
                }
            ]
            self._save_products()
    
    def _save_products(self):
        _save_json(SHOP_PRODUCTS_FILE, self.products)
    
    def _save_exchanges(self):
        _save_json(EXCHANGE_RECORDS_FILE, self.exchanges)
    
    def list_products(self, product_type: str = None) -> List[Dict]:
        result = [p for p in self.products if p.get('status') == 'active']
        if product_type:
            result = [p for p in result if p.get('type') == product_type]
        return result
    
    def exchange(self, session_id: str, product_id: str) -> Dict:
        product = None
        for p in self.products:
            if p['id'] == product_id:
                product = p
                break
        
        if not product:
            return {'success': False, 'error': '商品不存在'}
        
        if product.get('status') != 'active':
            return {'success': False, 'error': '商品已下架'}
        
        # 检查库存
        stock = product.get('stock', -1)
        if stock != -1 and stock <= 0:
            return {'success': False, 'error': '商品库存不足'}
        
        # 检查限购
        user_exchanges = [e for e in self.exchanges 
                         if e.get('session_id') == session_id and e.get('product_id') == product_id]
        if len(user_exchanges) >= product.get('limit_per_user', 999):
            return {'success': False, 'error': '已达到限购数量'}
        
        # 扣除积分
        result = self.points.consume_points(session_id, product['points_cost'], 
                                           f'兑换商品：{product["name"]}')
        if not result['success']:
            return result
        
        # 扣库存
        if stock > 0:
            product['stock'] -= 1
            self._save_products()
        
        # 记录兑换
        exchange = {
            'id': f"ex_{uuid.uuid4().hex[:8]}",
            'session_id': session_id,
            'product_id': product_id,
            'product_name': product['name'],
            'points_cost': product['points_cost'],
            'status': 'completed',
            'created_at': datetime.now().isoformat()
        }
        self.exchanges.append(exchange)
        self._save_exchanges()
        
        return {'success': True, 'exchange': exchange, 'product': product}
    
    def get_exchange_records(self, session_id: str) -> List[Dict]:
        result = [e for e in self.exchanges if e.get('session_id') == session_id]
        return sorted(result, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def admin_add_product(self, product: Dict) -> Dict:
        product['id'] = f"prod_{uuid.uuid4().hex[:6]}"
        product['created_at'] = datetime.now().isoformat()
        self.products.append(product)
        self._save_products()
        return product
    
    def admin_update_product(self, product_id: str, updates: Dict) -> Optional[Dict]:
        for p in self.products:
            if p['id'] == product_id:
                p.update(updates)
                self._save_products()
                return p
        return None

# ============================================================
# 单例服务实例
# ============================================================
_badcase_service = None
_model_call_service = None
_trace_service = None
_points_service = None
_checkin_service = None
_share_service = None
_level_service = None
_shop_service = None

def get_badcase_service() -> BadcaseService:
    global _badcase_service
    if _badcase_service is None:
        _badcase_service = BadcaseService()
    return _badcase_service

def get_model_call_service() -> ModelCallService:
    global _model_call_service
    if _model_call_service is None:
        _model_call_service = ModelCallService()
    return _model_call_service

def get_trace_service() -> TraceService:
    global _trace_service
    if _trace_service is None:
        _trace_service = TraceService()
    return _trace_service

def get_points_service() -> PointsService:
    global _points_service
    if _points_service is None:
        _points_service = PointsService()
    return _points_service

def get_checkin_service() -> CheckinService:
    global _checkin_service
    if _checkin_service is None:
        _checkin_service = CheckinService(get_points_service())
    return _checkin_service

def get_share_service() -> ShareService:
    global _share_service
    if _share_service is None:
        _share_service = ShareService(get_points_service())
    return _share_service

def get_level_service() -> LevelService:
    global _level_service
    if _level_service is None:
        _level_service = LevelService(get_points_service())
    return _level_service

def get_shop_service() -> ShopService:
    global _shop_service
    if _shop_service is None:
        _shop_service = ShopService(get_points_service())
    return _shop_service
