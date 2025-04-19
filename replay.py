from context.context_manager import ContextManager
import argparse

def main():
    parser = argparse.ArgumentParser(description="Replay or query context history from SQLite database.")
    parser.add_argument("--replay", action="store_true", help="Replay all context entries")
    parser.add_argument("--entry-type", help="Filter by entry type (e.g., tool_result, error)")
    parser.add_argument("--limit", type=int, help="Limit the number of entries to display")
    parser.add_argument("--start-time", help="Start timestamp (ISO format)")
    parser.add_argument("--end-time", help="End timestamp (ISO format)")
    parser.add_argument("--session", help="Filter by session ID")
    parser.add_argument("--list-sessions", action="store_true", help="List all available session IDs")
    args = parser.parse_args()

    context_manager = ContextManager()

    if args.list_sessions:
        sessions = context_manager.get_sessions()
        if sessions:
            print("Available sessions:")
            for idx, session_id in enumerate(sessions, 1):
                print(f"{idx}. {session_id}")
        else:
            print("No sessions found.")
        return
    
    if args.replay:
        print("Replaying context history:")
        context_manager.replay(limit=args.limit, entry_type=args.entry_type, session_id=args.session)
    else:
        print("Querying context:")
        entries = context_manager.query(
            start_time=args.start_time,
            end_time=args.end_time,
            entry_type=args.entry_type,
            session_id=args.session
        )
        for entry in entries:
            session_info = f" [Session: {entry['session_id']}]" if 'session_id' in entry else ""
            print(f"[{entry['timestamp']}]{session_info} {entry['data']}")

if __name__ == "__main__":
    main()