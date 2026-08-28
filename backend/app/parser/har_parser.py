import json
from urllib.parse import urlparse


class HARParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

        with open(file_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def extract_apis(self):
        inventory = []
        entries = self.data.get("log", {}).get("entries", [])

        for entry in entries:
            req = entry.get("request", {})
            res = entry.get("response", {})

            url_parsed = urlparse(req.get("url", ""))

            api_data = {
                "url": req.get("url"),
                "endpoint": url_parsed.path,
                "method": req.get("method"),
                "status_code": res.get("status"),
                "response_time": entry.get("time"),
                "content_type": res.get("content", {}).get("mimeType", ""),
                "headers": req.get("headers", []),
                "query_string": req.get("queryString", []),
                "post_data": req.get("postData", {}).get("text", ""),

                # Response body for Correlation Engine
                "response_body": res.get("content", {}).get("text", "")
            }

            inventory.append(api_data)

        return inventory