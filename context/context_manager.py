import sqlite3
import json
from datetime import datetime
import uuid

# In context/context_manager.py
VALID_ENTRY_TYPES = {"tool_result", "error", "human_input", "general", "custom_type"}


class ContextManager:
    def __init__(self, db_path="context.db"):
        self.db_path = db_path
        self.session_id = str(uuid.uuid4())
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database and create the context table if it doesn't exist."""
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

    def add(self, data, entry_type="general"):
        """Add a context entry to the database."""
        if entry_type not in VALID_ENTRY_TYPES:
            raise ValueError(f"Invalid entry_type: {entry_type}. Must be one of {VALID_ENTRY_TYPES}")
        timestamp = datetime.now().isoformat()
        data_json = json.dumps(data)  # Serialize data to JSON
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO context (timestamp, data, entry_type, session_id) VALUES (?, ?, ?, ?)",
                (timestamp, data_json, entry_type, self.session_id)
            )
            conn.commit()

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
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            # Return in the format expected by prompt_generator: [{"timestamp": ..., "data": ...}]
            return [
                {"timestamp": row[0], "data": json.loads(row[1])}
                for row in cursor.fetchall()
            ]

    def clear(self, current_session_only=True):
        """Clear context entries from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if current_session_only:
                cursor.execute("DELETE FROM context WHERE session_id = ?", (self.session_id,))
            else:
                cursor.execute("DELETE FROM context")
            conn.commit()

    def new_session(self):
        """Start a new session with a new session_id."""
        self.session_id = str(uuid.uuid4())
        return self.session_id

    def replay(self, limit=None, entry_type=None, session_id=None):
        """Replay context history by printing entries."""
        query = "SELECT timestamp, data, session_id FROM context"
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

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
        if not rows:
            print("No context entries found.")
            return

        current_session = None
        for timestamp, data_json, session in rows:
            data = json.loads(data_json)
            if current_session != session:
                current_session = session
                print(f"\n===== Session: {session} =====")
            print(f"[{timestamp}] {data}")

    def get_sessions(self):
        """Get a list of all session IDs."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id FROM context 
                GROUP BY session_id 
                ORDER BY MIN(timestamp)
            """)
            return [row[0] for row in cursor.fetchall()]

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

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [
                {"timestamp": row[0], "data": json.loads(row[1]), "session_id": row[2]}
                for row in cursor.fetchall()
            ]