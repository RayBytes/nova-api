import json

from helpers import chat

async def process_chunks(
    chunks,
    is_chat: bool,
    chat_id: int,
    target_request: dict,
    model: str=None,
):
    """This function processes the response chunks from the providers and yields them.
    """
    async for chunk in chunks:
        chunk = chunk.decode("utf8").strip()
        send = False

        if is_chat and '{' in chunk:
            data = json.loads(chunk.split('data: ')[1])
            chunk = chunk.replace(data['id'], chat_id)
            send = True

            if target_request['module'] == 'twa' and data.get('text'):
                chunk = await chat.create_chat_chunk(chat_id=chat_id, model=model, content=['text'])

            if (not data['choices'][0]['delta']) or data['choices'][0]['delta'] == {'role': 'assistant'}:
                send = False

        if send and chunk:
            yield chunk + '\n\n'
