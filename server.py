from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = "localhost"
serverPort = 8080
playerPositions = {}

def readFile(path: str) -> str:
	f = open(path, "r")
	content = f.read()
	f.close()
	return content

def writeFile(path: str, content: str):
	f = open(path, "w")
	f.write(content)
	f.close()

def get(path: str):
	if path == "/":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/plain"
			},
			"content": """"""
		}
	elif path.startswith("/getpos"):
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/plain"
			},
			"content": playerPositions[path[8:]]
		}
	elif path == "/players":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/plain"
			},
			"content": "\n".join(playerPositions.keys())
		}
	elif path == "/getworld":
		return {
			"status": 200,
			"headers": {
				"Content-Type": "text/plain"
			},
			"content": readFile("world.json")
		}
	else:
		print(f"Bad request to {path}")
		return {
			"status": 404,
			"headers": {},
			"content": "404"
		}

def post(path: str, body: bytes):
	global playerPositions
	if path.startswith("/setpos"):
		playerPositions[path[8:]] = body.decode()
		return {
			"status": 200,
			"headers": {},
			"content": ""
		}
	elif path == "/setworld":
		writeFile("world.json", body.decode())
		return {
			"status": 200,
			"headers": {},
			"content": ""
		}
	else:
		print(f"Bad POST to {path}")
		return {
			"status": 404,
			"headers": {},
			"content": "404"
		}

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		res = get(self.path)
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		c = res["content"]
		if type(c) == str: c = c.encode("utf-8")
		self.wfile.write(c)
	def do_POST(self):
		res = post(self.path, self.rfile.read(int(self.headers["Content-Length"])))
		self.send_response(res["status"])
		for h in res["headers"]:
			self.send_header(h, res["headers"][h])
		self.end_headers()
		self.wfile.write(res["content"].encode("utf-8"))
	def log_message(self, format: str, *args) -> None:
		return;
		if 400 <= int(args[1]) < 500:
			# Errored request!
			print(u"\u001b[31m", end="")
		print(args[0].split(" ")[0], "request to", args[0].split(" ")[1], "(status code:", args[1] + ")")
		print(u"\u001b[0m", end="")
		# don't output requests

if __name__ == "__main__":
	running = True
	webServer = HTTPServer((hostName, serverPort), MyServer)
	webServer.timeout = 1
	print("Server started http://%s:%s" % (hostName, serverPort))
	while running:
		try:
			webServer.handle_request()
		except KeyboardInterrupt:
			running = False
	webServer.server_close()
	print("Server stopped.")
