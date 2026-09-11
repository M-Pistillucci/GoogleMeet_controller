import asyncio
import json
import time
import threading
from typing import Dict, Optional, Callable, Any
from loguru import logger as log
import websockets
from websockets.server import WebSocketServerProtocol

from auth import AuthManager


class GoogleMeetController:
    """
    Handles WebSocket server for Google Meet Chrome extension communication.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.server = None
        self._stop_event = asyncio.Event()
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread = None
        self.connected = False

        # # Authentication managers
        self.auth_manager = AuthManager()
        # self.crypto = CryptoManager()
        # self.auth_manager = PairingManager()

        # Client management
        self.active_connection: Optional[WebSocketServerProtocol] = None
        self.extension_id: Optional[str] = None
        self.instance_id: Optional[str] = None

        # State tracking
        self.current_state = {
            "mic_enabled": False,
            "camera_enabled": False,
            "screen_sharing": False,
            "hand_raised": False,
            "in_meeting": False,
            "meeting_id": None,
            "meeting_name": None,
            "participant_count": 0,
        }

        # Callbacks for state updates
        self.state_update_callbacks: list[Callable] = []

        # Pending pairing approval requests (key: (extension_id, instance_id))
        self.pending_approval: Dict[tuple[str, str], asyncio.Future] = {}
        self._stop_event = asyncio.Event()

    def add_state_update_callback(self, callback: Callable[[Dict], None]):
        self.state_update_callbacks.append(callback)

    def remove_state_update_callback(self, callback: Callable[[Dict], None]):
        if callback in self.state_update_callbacks:
            self.state_update_callbacks.remove(callback)

    def _notify_state_update(self):
        state_copy = self.current_state.copy()
        for callback in self.state_update_callbacks:
            try:
                callback(state_copy)
            except Exception as e:
                log.error(f"Error in state update callback: {e}")

    def revoke_instance(self, extension_id: str, instance_id: str):
        self.auth_manager.revoke_instance(extension_id, instance_id)
        if self.extension_id == extension_id and self.instance_id == instance_id and self.active_connection:
            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self.active_connection.close(1000, "Instance revoked"),
                    self.loop
                )

    def request_approval(self, pairing_request: Any) -> asyncio.Future:
        key = (pairing_request.extension_id, pairing_request.instance_id)

        if self.auth_manager.is_authorized(pairing_request.extension_id, pairing_request.instance_id):
            future = self.loop.create_future()
            future.set_result(True)
            return future

        future = self.loop.create_future()
        self.pending_approval[key] = future
        log.info(f"Approval requested for {pairing_request.extension_id} (instance: {pairing_request.instance_id})")
        return future

    def approve_instance(self, extension_id: str, instance_id: str):
        self.auth_manager.approve_instance(extension_id, instance_id)
        key = (extension_id, instance_id)
        if key in self.pending_approval:
            future = self.pending_approval.pop(key)
            if not future.done():
                self.loop.call_soon_threadsafe(future.set_result, True)
        log.info(f"Instance approved: {extension_id}/{instance_id}")

    def deny_instance(self, extension_id: str, instance_id: str):
        self.auth_manager.deny_instance(extension_id, instance_id)
        key = (extension_id, instance_id)
        if key in self.pending_approval:
            future = self.pending_approval.pop(key)
            if not future.done():
                self.loop.call_soon_threadsafe(future.set_result, False)
        log.info(f"Instance denied: {extension_id}/{instance_id}")

    def _verify_message(self, data: Dict) -> Optional[Dict]:
        extension_id = data.get("extension_id")
        instance_id = data.get("instance_id")
        token = data.get("token")

        if not extension_id or not instance_id or not token:
            log.error("Missing required fields in message")
            return None

        if not self.auth_manager.is_authorized(extension_id, instance_id):
            log.error(f"Unauthorized instance: {extension_id}/{instance_id}")
            return None

        public_key = self.auth_manager.get_public_key(extension_id, instance_id)
        if not public_key:
            log.error(f"No public key found for {extension_id}/{instance_id}")
            return None

        payload = self.crypto.verify_jws(token, public_key)
        if not payload:
            log.error(f"JWS verification failed for {extension_id}/{instance_id}")
            return None

        if payload.get("instance_id") != instance_id:
            log.error("Instance ID mismatch in JWT payload")
            return None

        return payload

    async def _handle_handshake(self, websocket: WebSocketServerProtocol, data: Dict) -> bool:
        # Accetta qualsiasi handshake senza verificare chiavi o chiedere approvazioni
        self.extension_id = data.get("extension_id", "my_extension")
        self.instance_id = data.get("instance_id", "browser_1")
        self.active_connection = websocket
        self.connected = True

        await websocket.send(json.dumps({
            "type": "handshake_success",
            "message": "Authorized"
        }))
        log.info("Handshake semplificato completato con successo!")
        return True

    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str):
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "handshake":
                await self._handle_handshake(websocket, data)
                return

            # Accetta direttamente i messaggi senza verificare la firma crypto
            if msg_type in ("state", "heartbeat"):
                await self._handle_state_update(data)
                if msg_type == "heartbeat":
                    await websocket.send(json.dumps({"type": "heartbeat_ack"}))
            elif msg_type == "command_response":
                log.debug(f"Command response: {data}")

        except Exception as e:
            log.error(f"Error handling message: {e}")

    async def _handle_state_update(self, data: Dict):
        state_data = data.get("data", {})
        for key in self.current_state.keys():
            if key in state_data:
                self.current_state[key] = state_data[key]

        if not self.current_state.get("in_meeting", False):
            self.current_state["meeting_id"] = None
            self.current_state["meeting_name"] = None
            self.current_state["participant_count"] = 0

        self._notify_state_update()
        log.debug(f"State updated: {self.current_state}")

    async def _handle_client(self, websocket: WebSocketServerProtocol):
        client_addr = websocket.remote_address
        log.info(f"Client connected: {client_addr}")

        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            log.info(f"Client disconnected: {client_addr}")
        finally:
            if self.active_connection == websocket:
                self.active_connection = None
                self.extension_id = None
                self.instance_id = None
                self.connected = False

                self.current_state = {
                    "mic_enabled": False,
                    "camera_enabled": False,
                    "screen_sharing": False,
                    "hand_raised": False,
                    "in_meeting": False,
                    "meeting_id": None,
                    "meeting_name": None,
                    "participant_count": 0,
                }
                self._notify_state_update()

    async def send_command(self, action: str, data: Optional[Dict] = None) -> bool:
        if not self.active_connection:
            log.warning("Cannot send command: no active connection")
            return False

        try:
            command = {
                "type": "command",
                "action": action,
                "data": data or {}
            }
            await self.active_connection.send(json.dumps(command))
            log.debug(f"Command sent: {action}")
            return True
        except Exception as e:
            log.error(f"Error sending command: {e}")
            return False

    async def _run_server(self):
        try:
            async with websockets.serve(self._handle_client, self.host, self.port) as server:
                self.server = server
                log.info(f"WebSocket server started on {self.host}:{self.port}")
                await self._stop_event.wait()
        except Exception as e:
            log.error(f"Server error: {e}")

    def start(self):
        self._thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self._thread.start()
        # if self.loop and self.loop.is_running():
        #     log.warning("Server already running")
        #     return
        #
    def _run_async_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._run_server())

        # def run_loop():
        #     self.loop = asyncio.new_event_loop()
        #     asyncio.set_event_loop(self.loop)
        #     self._stop_event = asyncio.Event()
        #     self.loop.run_until_complete(self._run_server())

        # thread = threading.Thread(target=run_loop, daemon=True, name="google_meet_ws_server")
        # thread.start()
        # log.info("WebSocket server thread started")

    def stop(self):
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self._stop_event.set)
            log.info("WebSocket server stopping signal sent")

    def get_state(self) -> Dict[str, Any]:
        return self.current_state.copy()

    def is_connected(self) -> bool:
        return self.connected

    def is_in_meeting(self) -> bool:
        return self.current_state.get("in_meeting", False)

    def toggle_microphone(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.send_command("toggle_mic"), self.loop)

    def toggle_camera(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.send_command("toggle_camera"), self.loop)

    def toggle_hand(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.send_command("toggle_hand"), self.loop)

    def send_reaction(self, reaction: str):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.send_command("send_reaction", {"reaction": reaction}), self.loop)

    def toggle_screen_share(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.send_command("toggle_screen_share"), self.loop)

    def leave_call(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.send_command("leave_call"), self.loop)

    def get_pending_pairing_requests(self) -> list[Dict[str, str]]:
        return self.auth_manager.get_pending_pairing_requests()

    def get_authorized_instances(self) -> list[Dict[str, str]]:
        return self.auth_manager.get_authorized_instances()
