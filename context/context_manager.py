import sqlite3
import json
from datetime import datetime
import uuid
from utils.logger import logger

# In context/context_manager.py
VALID_ENTRY_TYPES = {"tool_result", "error", "human_input", "general", "custom_type","stop"}


class ContextManager:
    def __init__(self, db_path="context.db"):
        self.db_path = db_path
        self.session_id = str(uuid.uuid4())
        logger.debug(f"初始化上下文管理器: 数据库路径={db_path}, 初始会话ID={self.session_id}")
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database and create the context table if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS context (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        data TEXT NOT NULL,
                        entry_type TEXT NOT NULL,
                        session_id TEXT NOT NULL
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON context (timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_entry_type ON context (entry_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON context (session_id)")
                conn.commit()
                logger.debug(f"数据库初始化成功: {self.db_path}")
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            raise

    def add(self, data, entry_type="general"):
        """Add a context entry to the database."""
        if entry_type not in VALID_ENTRY_TYPES:
            error_msg = f"无效的条目类型: {entry_type}. 必须是 {VALID_ENTRY_TYPES} 之一"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        timestamp = datetime.now().isoformat()
        data_json = json.dumps(data)  # Serialize data to JSON
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO context (timestamp, data, entry_type, session_id) VALUES (?, ?, ?, ?)",
                    (timestamp, data_json, entry_type, self.session_id)
                )
                entry_id = cursor.lastrowid
                conn.commit()
                logger.debug(f"添加上下文条目: ID={entry_id}, 类型={entry_type}, 会话={self.session_id}")
                return entry_id
        except Exception as e:
            logger.error(f"添加上下文条目失败: {str(e)}")
            raise

    def get(self, limit=None, entry_type=None, all_sessions=False):
        """Retrieve context entries from the database."""
        query = "SELECT timestamp, data FROM context"
        params = []
        conditions = []

        if not all_sessions:
            conditions.append("session_id = ?")
            params.append(self.session_id)

        if entry_type:
            conditions.append("entry_type = ?")
            params.append(entry_type)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC"
        if limit!=None:
            query += " LIMIT ?"
            params.append(limit)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                logger.debug(f"检索上下文条目: 条数={len(results)}, 限制={limit}, 类型={entry_type}, 所有会话={all_sessions}")
                # Return in the format expected by prompt_generator: [{"timestamp": ..., "data": ...}]
                return [
                    {"timestamp": row[0], "data": json.loads(row[1])}
                    for row in results
                ]
        except Exception as e:
            logger.error(f"检索上下文条目失败: {str(e)}")
            raise

    def clear(self, current_session_only=True):
        """Clear context entries from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if current_session_only:
                    cursor.execute("DELETE FROM context WHERE session_id = ?", (self.session_id,))
                    logger.debug(f"清除当前会话({self.session_id})的上下文条目")
                else:
                    cursor.execute("DELETE FROM context")
                    logger.debug("清除所有会话的上下文条目")
                deleted_rows = cursor.rowcount
                conn.commit()
                return deleted_rows
        except Exception as e:
            logger.error(f"清除上下文条目失败: {str(e)}")
            raise

    def new_session(self):
        """Start a new session with a new session_id."""
        old_session = self.session_id
        self.session_id = str(uuid.uuid4())
        logger.debug(f"创建新会话: 旧会话={old_session}, 新会话={self.session_id}")
        return self.session_id

    def replay(self, limit=None, entry_type=None, session_id=None):
        """Replay context history by printing entries."""
        query = "SELECT timestamp, data, session_id, entry_type FROM context"
        params = []
        conditions = []

        if session_id:
            conditions.append("session_id = ?")
            params.append(session_id)

        if entry_type:
            conditions.append("entry_type = ?")
            params.append(entry_type)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp ASC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
            if not rows:
                logger.info("未找到上下文条目")
                return

            logger.debug(f"回放上下文历史: 条数={len(rows)}, 限制={limit}, 类型={entry_type}, 会话={session_id}")
            logger.info(f"\n===== 开始回放上下文历史 =====")
            
            current_session = None
            for timestamp, data_json, session, entry_type in rows:
                data = json.loads(data_json)
                if current_session != session:
                    current_session = session
                    logger.info(f"\n----- 会话: {session} -----")
                
                # 根据不同的条目类型格式化输出
                if entry_type == "tool_result":
                    tool_name = data.get("tool", "未知工具")
                    tool_input = data.get("input", "")
                    result = data.get("result", "")
                    logger.info(f"[{timestamp}] 工具执行: {tool_name}({tool_input})")
                    logger.result(f"{result}")
                elif entry_type == "error":
                    error_msg = data.get("error", "未知错误")
                    logger.info(f"[{timestamp}] 错误: {error_msg}")
                elif entry_type == "human_input":
                    human_input = data.get("human_input", "")
                    logger.info(f"[{timestamp}] 人工输入: {human_input}")
                elif entry_type == "stop":
                    result = data.get("result", "")
                    logger.info(f"[{timestamp}] 最终结果:")
                    logger.result(f"{result}")
                else:
                    logger.info(f"[{timestamp}] {entry_type}: {data}")
            
            logger.info(f"\n===== 上下文历史回放结束 =====")    
            return rows
        except Exception as e:
            logger.error(f"回放上下文历史失败: {str(e)}")
            raise

    def get_sessions(self):
        """Get a list of all session IDs."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id FROM context 
                    GROUP BY session_id 
                    ORDER BY MIN(timestamp)
                """)
                sessions = [row[0] for row in cursor.fetchall()]
                logger.debug(f"获取会话列表: 数量={len(sessions)}")
                return sessions
        except Exception as e:
            logger.error(f"获取会话列表失败: {str(e)}")
            raise

    def query(self, start_time=None, end_time=None, entry_type=None, session_id=None):
        """Query context entries with optional time range, entry type, and session filters."""
        query = "SELECT timestamp, data, session_id FROM context"
        params = []
        conditions = []

        if session_id:
            conditions.append("session_id = ?")
            params.append(session_id)
        
        if entry_type:
            conditions.append("entry_type = ?")
            params.append(entry_type)
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time)
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp ASC"

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                logger.debug(f"查询上下文条目: 条数={len(results)}, 开始时间={start_time}, 结束时间={end_time}, 类型={entry_type}, 会话={session_id}")
                return [
                    {"timestamp": row[0], "data": json.loads(row[1]), "session_id": row[2]}
                    for row in results
                ]
        except Exception as e:
            logger.error(f"查询上下文条目失败: {str(e)}")
            raise