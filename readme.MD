# Real-Time Chat Application API

## User websocket connection

<ws://127.0.0.1:8000/ws/chat/recipient_id/?auth_token=token>

This endpoint is used to establish a websocket connection with rtc_api.

### Response

``` json
{
    "message": "Connected to recipient_id!"
}

 ```

## User sending message

<ws://127.0.0.1:8000/ws/chat/recipient_id/?auth_token=token>

### Messages

```json
{
    "message" : "Content of message"
}
```
