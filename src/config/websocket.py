
from fastapi import WebSocket
from fastapi.params import Depends

from chat.models import ChatMessage
from chat.repository import ChatRepository





class WebSocketConnectionManager:
    def __init__(self):
        self.connections: dict[WebSocket, tuple[int: int]] = dict()

    def __call__(self, chat_repo: ChatRepository = Depends()):
        self.chat_repo = chat_repo
        return self

    async def _send_message(self, websocket: WebSocket, message: ChatMessage, me_id: int):

        if message.user_id == me_id:
            await self._send_my_messages(websocket=websocket, content=message.content)
        else:
            await self._send_friend_messages(websocket=websocket, content=message.content)


    async def _send_my_messages(self, websocket:WebSocket, content: str):
        await websocket.send_text(f" ME > {content}")

    async def _send_friend_messages(self, websocket:WebSocket, content: str):
        await websocket.send_text(f" friend > {content}")


    async def _get_context(self, websocket: WebSocket) -> tuple[int, int]:
        return self.connections[websocket]

    async def _init_messages(self, websocket: WebSocket):
        room_id, user_id = await self._get_context(websocket=websocket)

        messages = await self.chat_repo.get_messages_by_room(room_id=room_id)
        for message in messages:
            await self._send_message(
                websocket=websocket, message=message, me_id=user_id
            )

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        await websocket.accept()  # 웹소켓 통신 허용
        self.connections[websocket] =  room_id, user_id
        await self._init_messages(websocket=websocket)

    # 서버에서 관리 중인 모든 ws 연결에 메세지를 전파
    async def broadcast(self, websocket: WebSocket, content: str):

        # 지금 메세지를 보낸 user_id
        room_id, user_id = await self._get_context(websocket=websocket)

        # 새로운 메시지 DB에 저장
        message = ChatMessage.create(room_id=room_id, user_id=user_id, content=content)
        await self.chat_repo.save(message=message)

        # 관리 중인 모든 ws 연결
        for conn, (conn_room_id, conn_user_id) in self.connections.items():
            if conn_user_id == user_id:
                await self._send_my_messages(websocket=conn, content=content )
            else:
                await self._send_friend_messages(websocket=conn, content=content)

    def disconnect(self, websocket: WebSocket):
        self.connections.pop(websocket)


ws_connection_manager = WebSocketConnectionManager()




        # 이전 메세지를 최신순으로 전부 조회
        # messages = await self.chat_repo.get_message()
        # for message in messages:
        #     await self._send_message(
        #         websocket=websocket, message=message, me_id=user_id
        #     )
        #

            # # 내가 보낸 메세지만 출력
            # if message.user_id == user_id:
            #     await websocket.send_text(f" ME > {message.content}")
            # # 다른 사람이 보낸 메세지
            # else:
            #     await websocket.send_text(f" Friend > {message.content}")
