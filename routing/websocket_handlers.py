import json
import typing as t

from starletteapi.exceptions import WebSocketRequestValidationError
from starlette.types import Message

from starletteapi import status
if t.TYPE_CHECKING:
    from starletteapi.context import ExecutionContext
    from starletteapi.route_models import WebsocketParameterModel
    from starletteapi.controller import ControllerBase
    from starletteapi.websockets import WebSocket


class WebSocketExtraHandler:
    def __init__(
            self,
            on_receive: t.Callable,
            encoding: str = 'json',  # May be "text", "bytes", or "json".
            on_connect: t.Callable = None,
            on_disconnect: t.Callable = None,
            route_parameter_model: 'WebsocketParameterModel' = None,
    ):
        self.on_receive = on_receive
        self.encoding = encoding
        self.on_disconnect = on_disconnect
        self.on_connect = on_connect
        self.route_parameter_model = route_parameter_model

    async def dispatch(self, context: 'ExecutionContext', **receiver_kwargs: t.Any) -> None:
        websocket = context.switch_to_websocket()
        await self.execute_on_connect(context=context)
        close_code = status.WS_1000_NORMAL_CLOSURE

        try:
            while True:
                message = await websocket.receive()
                if message["type"] == "websocket.receive":
                    data = await self.decode(websocket, message)
                    await self.execute_on_receive(context=context, data=data, **receiver_kwargs)
                elif message["type"] == "websocket.disconnect":
                    close_code = int(message.get("code", status.WS_1000_NORMAL_CLOSURE))
                    break
        except Exception as exc:
            close_code = status.WS_1011_INTERNAL_ERROR
            raise exc
        finally:
            await self.execute_on_disconnect(context=context, close_code=close_code)

    async def _resolve_receiver_dependencies(
            self,  context: 'ExecutionContext', data: t.Any
    ) -> t.Dict:
        extra_kwargs, errors = await self.route_parameter_model.resolve_ws_body_dependencies(
            ctx=context, body_data=data
        )
        if errors:
            exc = WebSocketRequestValidationError(errors)
            await context.switch_to_websocket().send_json(
                dict(code=status.WS_1003_UNSUPPORTED_DATA, errors=exc.errors())
            )
            raise exc
        return extra_kwargs

    async def execute_on_receive(self, *, context: 'ExecutionContext', data: t.Any, **receiver_kwargs: t.Any):
        extra_kwargs = await self._resolve_receiver_dependencies(context=context, data=data)

        receiver_kwargs.update(extra_kwargs)
        await self.on_receive(**receiver_kwargs)

    async def execute_on_connect(self, *, context: 'ExecutionContext'):
        if self.on_connect:
            await self.on_connect(context.switch_to_websocket())
            return
        await context.switch_to_websocket().accept()

    async def execute_on_disconnect(self, *, context: 'ExecutionContext', close_code: int):
        if self.on_disconnect:
            await self.on_disconnect(context.switch_to_websocket(), close_code)

    async def decode(self, websocket: 'WebSocket', message: Message) -> t.Any:
        if self.encoding == "text":
            if "text" not in message:
                await websocket.send_json(
                    dict(code=status.WS_1003_UNSUPPORTED_DATA,
                         details="Expected text websocket messages, but got bytes")
                )
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                raise RuntimeError("Expected text websocket messages, but got bytes")
            return message["text"]

        elif self.encoding == "bytes":
            if "bytes" not in message:
                await websocket.send_json(
                    dict(code=status.WS_1003_UNSUPPORTED_DATA,
                         details="Expected bytes websocket messages, but got text")
                )
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                raise RuntimeError("Expected bytes websocket messages, but got text")
            return message["bytes"]

        elif self.encoding == "json":
            if message.get("text") is not None:
                text = message["text"]
            else:
                text = message["bytes"].decode("utf-8")

            try:
                return json.loads(text)
            except json.decoder.JSONDecodeError:
                await websocket.send_json(
                    dict(code=status.WS_1003_UNSUPPORTED_DATA,
                         details="Malformed JSON data received.")
                )
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                raise RuntimeError("Malformed JSON data received.")

        assert (
            self.encoding is None
        ), f"Unsupported 'encoding' attribute {self.encoding}"
        return message["text"] if message.get("text") else message["bytes"]


class ControllerWebSocketExtraHandler(WebSocketExtraHandler):
    def __init__(
            self,
            controller_instance: 'ControllerBase',
            **kwargs: t.Any
    ):
        super().__init__(**kwargs)
        self.controller_instance = controller_instance

    async def execute_on_receive(self, *, context: 'ExecutionContext', data: t.Any, **receiver_kwargs: t.Any):
        extra_kwargs = await self._resolve_receiver_dependencies(context=context, data=data)

        receiver_kwargs.update(extra_kwargs)
        await self.on_receive(self.controller_instance, **receiver_kwargs)

    async def execute_on_connect(self, *, context: 'ExecutionContext'):
        if self.on_connect:
            await self.on_connect(self.controller_instance, context.switch_to_websocket())
            return
        await context.switch_to_websocket().accept()

    async def execute_on_disconnect(self, *, context: 'ExecutionContext', close_code: int):
        if self.on_disconnect:
            await self.on_disconnect(self.controller_instance, context.switch_to_websocket(), close_code)
