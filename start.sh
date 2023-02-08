nohup python3 grpc_server.py >/dev/null 2>&1 &

uvicorn http_server:app --reload --host 0.0.0.0 --port 8000
