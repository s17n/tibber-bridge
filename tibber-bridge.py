import tibber.const
import asyncio
import aiohttp
import tibber
import os
import paho.mqtt.client as mqtt
import logging
import json

log = logging.getLogger('logger')
log.setLevel(logging.INFO)

formatter = logging.Formatter('%(message)s')

fh = logging.FileHandler('tibber-bridge.log', mode='w', encoding='utf-8')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
log.addHandler(fh)

def _callback(pkg):
    data = pkg.get("data")
    if data is None:
        return
    liveMeasurement = data.get("liveMeasurement")#.get("power")
    client.publish("tibber/liveMeasurement", json.dumps(liveMeasurement))
    #print(liveMeasurement)

async def run():

    tibber_api_token = os.environ['TIBBER_API_TOKEN']
    log.info(f'Tibber API token: {tibber_api_token}')

    async with aiohttp.ClientSession() as session:
        tibber_connection = tibber.Tibber(tibber_api_token, websession=session, user_agent="user_agent")
        await tibber_connection.update_info()

        home = tibber_connection.get_homes()[0]
        await home.update_info()
        await home.update_price_info()
        
        #if not home.rt_subscription_running:
        await home.rt_subscribe(_callback)
        await asyncio.sleep(10)
        
        while(True):
            
            await home.update_info_and_price_info()
            await asyncio.sleep(10)

log.info('tibber-bridge v0.0.1 12/02/2023')

tibber_mqtt_broker = os.environ['TIBBER_MQTT_BROKER']
log.info(f'Tibber MQTT broker: {tibber_mqtt_broker}')

client = mqtt.Client()
client.connect(tibber_mqtt_broker, 1883, 60)

if __name__ == '__main__':
    asyncio.run(run())

client.disconnect()