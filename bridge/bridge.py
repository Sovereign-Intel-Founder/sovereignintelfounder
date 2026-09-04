import http.server
import subprocess
import json
import os

PORT = 8889

class BridgeHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode('utf-8'))
            req_id = data.get('id', 1)
            method = data.get('method', '')

            # 1. MCP Initialization Handshake
            if method == 'initialize':
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "sip-comprehensive-bridge", "version": "2.0.0"}
                    },
                    "id": req_id
                }
            # 2. MCP Tool Listing (Exposing full execution and file inspection tools)
            elif method == 'tools/list':
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "tools": [
                            {
                                "name": "run_command",
                                "description": "Execute any shell command, compilation, or deployment script on the server workspace.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "command": {"type": "string", "description": "The shell command to execute"}
                                    },
                                    "required": ["command"]
                                }
                            },
                            {
                                "name": "read_file",
                                "description": "Read contents of a file within the workspace.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "path": {"type": "string", "description": "Absolute file path"}
                                    },
                                    "required": ["path"]
                                }
                            }
                        ]
                    },
                    "id": req_id
                }
            # 3. Tool Execution Handler
            elif method == 'tools/call':
                params = data.get('params', {})
                tool_name = params.get('name')
                arguments = params.get('arguments', {})

                if tool_name == 'run_command':
                    command = arguments.get('command', 'ls -la /home/joshua445/tollbridge_system')
                    full_cmd = f"bash -c '{command}'"
                    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=120)
                    output_text = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nExit Code: {result.returncode}"
                    
                    response = {
                        "jsonrpc": "2.0",
                        "result": {
                            "content": [{"type": "text", "text": output_text}],
                            "isError": result.returncode != 0
                        },
                        "id": req_id
                    }
                elif tool_name == 'read_file':
                    file_path = arguments.get('path')
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            file_content = f.read()
                        response = {
                            "jsonrpc": "2.0",
                            "result": {
                                "content": [{"type": "text", "text": file_content}],
                                "isError": False
                            },
                            "id": req_id
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "result": {
                                "content": [{"type": "text", "text": f"Error: File not found -> {file_path}"}],
                                "isError": True
                            },
                            "id": req_id
                        }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": f"Tool not found: {tool_name}"},
                        id: req_id
                    }
            # Fallback for generic JSON-RPC direct payloads
            else:
                params = data.get('params', {})
                command = params.get('arguments', {}).get('command', params.get('command', data.get('command', 'ls -la /home/joshua445/tollbridge_system')))
                full_cmd = f"bash -c '{command}'"
                result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=120)
                
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [{"type": "text", "text": result.stdout + "\n" + result.stderr}],
                        "isError": result.returncode != 0
                    },
                    "id": req_id
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": 1
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), BridgeHandler)
    print(f"Comprehensive MCP Bridge running on port {PORT}...")
    server.serve_forever()
EOF
