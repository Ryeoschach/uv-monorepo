from datetime import datetime, timezone

def get_utc_timestamp():
  """
  返回当前 UTC 时间戳，格式为 ISO 8601。
  示例格式：'2025-04-21T11:11:28Z'
  """
  return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

if __name__ == "__main__":
  print(get_utc_timestamp())
