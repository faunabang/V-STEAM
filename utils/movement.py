import asyncio
import pyvts

async def connect_auth(myvts):
    await myvts.connect()
    await myvts.request_authenticate_token()
    await myvts.request_authenticate()
    await myvts.close()

async def trigger(myvts, feeling):
    await myvts.connect()
    await myvts.request_authenticate()
    response_data = await myvts.request(myvts.vts_request.requestHotKeyList())
    # print(response_data)
    hotkey_list = []
    for hotkey in response_data["data"]["availableHotkeys"]:
        hotkey_list.append(hotkey["name"])
    # print(hotkey_list)
    send_hotkey_request = myvts.vts_request.requestTriggerHotKey(feeling)
    await myvts.request(send_hotkey_request)  # send request to play 'My Animation 1'
    await myvts.close()

if __name__ == "__main__":
    myvts = pyvts.vts()
    try:
        asyncio.run(connect_auth(myvts))
        asyncio.run(trigger(myvts, 'excited'))
    except:
        print()