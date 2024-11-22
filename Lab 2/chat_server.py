import asyncio
import websockets
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# In-memory data structure to store chat room users
chat_rooms = {"default_room": set()}  # Example chat room

async def chat_handler(websocket):
    """
    Handle WebSocket connections for the chat room.
    """
    # Default room and client initialization
    room_name = "default_room"
    chat_rooms[room_name].add(websocket)

    try:
        # Notify the user joined
        await broadcast_message(room_name, f"A user joined the chat room.")

        async for message in websocket:
            # Parse the received message
            if message.startswith("join_room:"):
                _, room_name = message.split(":", 1)
                room_name = room_name.strip()

                # Join the new room
                await join_room(websocket, room_name)

            elif message.startswith("send_msg:"):
                msg_content = message.split(":", 1)[1].strip()
                await broadcast_message(room_name, msg_content)

            elif message == "leave_room":
                await leave_room(websocket, room_name)
                break

    except websockets.ConnectionClosed:
        print("A user disconnected.")
    finally:
        # Cleanup on disconnect
        await leave_room(websocket, room_name)


async def join_room(websocket, room_name):
    """
    Join a new chat room.
    """
    for room in chat_rooms.values():
        room.discard(websocket)  # Leave any previous room
    if room_name not in chat_rooms:
        chat_rooms[room_name] = set()  # Create room if not exists
    chat_rooms[room_name].add(websocket)
    await broadcast_message(room_name, "A user joined the room.")

async def leave_room(websocket, room_name):
    """
    Leave the current chat room.
    """
    if room_name in chat_rooms:
        chat_rooms[room_name].discard(websocket)
        if len(chat_rooms[room_name]) == 0:
            del chat_rooms[room_name]
        else:
            await broadcast_message(room_name, "A user left the room.")

async def broadcast_message(room_name, message):
    """
    Send a message to all users in a specific chat room.
    """
    if room_name in chat_rooms:
        websockets_list = list(chat_rooms[room_name])
        if websockets_list:
            await asyncio.gather(*[ws.send(message) for ws in websockets_list])

# HTTP Server (Static Files)
class StaticServerHandler(SimpleHTTPRequestHandler):
    """
    HTTP server for serving a simple UI or API endpoint.
    """
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"  # Serve a default HTML page
        return super().do_GET()

def run_http_server():
    """
    Start the HTTP server in a separate thread.
    """
    httpd = HTTPServer(("127.0.0.1", 8080), StaticServerHandler)
    print("HTTP server running at http://127.0.0.1:8080")
    httpd.serve_forever()

# WebSocket Server
async def run_websocket_server():
    """
    Start the WebSocket server on port 8000.
    """
    async with websockets.serve(chat_handler, "127.0.0.1", 8000):
        print("WebSocket server running at ws://127.0.0.1:8000")
        await asyncio.Future()  # Keep the server running

# Run both servers in separate threads
def main():
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Run WebSocket server on the main thread
    asyncio.run(run_websocket_server())

if __name__ == "__main__":
    main()
