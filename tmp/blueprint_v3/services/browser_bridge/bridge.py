
class BrowserBridge:

    def open_session(self, provider):
        print(f"Opening browser session for {provider}")

    def send_message(self, session_id, message):
        print(f"Sending message to external chat: {message}")

    def read_response(self):
        return "External model response"
