import json
from pathlib import Path
import time

class RequestsRepository:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.data_file = self.base_dir / "json" / "requests.json"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self.data_file.write_text("[]", encoding="utf-8")

    def create_request(self, username, message, request_type="sensor_change"):
        try:
            content = self.data_file.read_text(encoding="utf-8")
            data = json.loads(content)
        except:
            data = []

        new_req = {
            "id": int(time.time() * 1000),
            "user": username,
            "type": request_type,
            "message": message,
            "status": "PENDING",
            "timestamp": time.time()
        }
        data.append(new_req)
        self.data_file.write_text(json.dumps(data, indent=4), encoding="utf-8")

    def get_all_requests(self):
        try:
            content = self.data_file.read_text(encoding="utf-8")
            return json.loads(content)
        except:
            return []

    def update_request_status(self, request_id, new_status):
        requests = self.get_all_requests()
        for req in requests:
            if req.get("id") == request_id:
                req["status"] = new_status
                break
        self.data_file.write_text(json.dumps(requests, indent=4), encoding="utf-8")
