
class SessionRegistry:

    def __init__(self):
        self.sessions = {}

    def create_session(self, session):
        self.sessions[session["id"]] = session
        return session

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def list_sessions(self):
        return list(self.sessions.values())
