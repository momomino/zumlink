from enum import Enum
import asyncio
from time import sleep
import aiohttp

GATEWAY_IP="192.168.0.100"
ENDPOINT_IP="192.168.0.99"


async def main():

    # Setup the radios
    gateway = Radio(GATEWAY_IP,"Gateway")
    endpoint = Radio(ENDPOINT_IP,"Endpoint")

    radios = [gateway, endpoint]

    await print_radios(radios)

    gatewayDiagnotics = await gateway.get_local_diagnostics()
    gateway_threshold = int(gatewayDiagnotics["signalLevel"])
    gateway_margin = int(gatewayDiagnotics["signalMargin"])

    # gateway_threshold = 80 # TO FORCE CHANGE

    if gateway_margin < gateway_threshold:
        print("Gatway Margin under minimum threshold")
        await change_data_rates([endpoint, gateway],DataRate.RATE_115_2K)
        await print_radios(radios)
    else:
        print("Gatway Margin above minimum threshold")
        await change_data_rates([endpoint, gateway],DataRate.RATE_500K)
        await print_radios(radios)

    print("Cleanup radio sessions")
    for radio in radios:
        await radio.close()
        

async def print_radios(radios):
    """ Prints information about radios """
    # Todo: would be better to use asyncio.gather to run these concurrently
    for radio in radios:
        await radio.print()

async def change_data_rates(radios, newDataRate):
    """ Change the data rate of radios """
    for radio in radios:
        print("Changing data rate on {} to {}".format(radio.name, newDataRate.name))
        asyncio.ensure_future(radio.set_data_rate(newDataRate.value))


class DataRate(Enum):
    """ ENUM representing ZUM radio Data Rates """
    RATE_4M = "RATE_4M"
    RATE_1M = "RATE_1M"
    RATE_1_5M_BETA_FEATURE = "RATE_1.5M_BETA_FEATURE"
    RATE_500K = "RATE_500K"
    RATE_250K = "RATE_250K"
    RATE_115_2K = "RATE_115.2K"
    
class Radio:
    """ This class is here to provide a wrapper around the ZUM rest api"""
    def __init__(self, ip_address, name="default", user='admin', password='admin'):  # name="default" gives the name parameter a default value of "default"
        self.name = name
        self.ip_address = ip_address
        self.user = user
        self.password = password
        self.base_url = 'http://{}/cli/'.format(self.ip_address)
        self._session = aiohttp.ClientSession(auth=aiohttp.BasicAuth(self.user,self.password))

    # LOCAL DIAGNOSTICS PAGE
    async def get_local_diagnostics(self):
        """ Gets local diagnostics """
        response = await self.__issue_request('localdiagnostics')
        return response["localDiagnostics"]
    
    async def get_signal_margin(self):
        """ Gets link margin from radio """
        response = await self.get_local_diagnostics()
        return int(response["signalMargin"])

    async def get_signal_level(self):
        """ Gets signal level from radio """
        response = await self.get_local_diagnostics()
        return int(response["signalLevel"])

    async def get_noise_level(self):
        """ Gets signal level from radio """
        response = await self.get_local_diagnostics()
        return int(response["NoiseLevel"])

    # RADIO SETTINGS PAGE
    async def get_radio_settings(self):
        """ Gets radio settings """
        response = await self.__issue_request('radioSettings')
        return response["radioSettings"]

    async def get_data_rate(self):
        """ Gets data rate from radio """
        response = await  self.get_radio_settings()
        return response["rfDataRate"]

    async def set_data_rate(self,newDataRate):
        """ Sets Data Rate for radio """
        response = await self.__issue_request('radioSettings.rfDataRate={}'.format(newDataRate))
        return response["radioSettings"]["rfDataRate"]

    # DATA PATH PAGE
    async def get_data_path(self):
        """ Gets data path """
        response = await self.__issue_request('dataPath')
        return response["dataPath"]

    async def get_min_signal_margin_threshold(self):
        """ Gets link margin from radio """
        response = await self.get_data_path()
        return int(response["routeMinSignalMarginThresh"])

    async def print(self):
        """ Print summary for Radio """
        data_rate = asyncio.Task(self.get_data_rate())
        diagnostics = asyncio.Task(self.get_local_diagnostics())
        marginThreshold = asyncio.Task(self.get_min_signal_margin_threshold())
        await asyncio.gather(
            data_rate,
            diagnostics,
            marginThreshold
        )
        print("-------",self.name,"--------")
        print("  ","Data Rate\t",data_rate.result())
        print("  ","Margin Threshold\t",marginThreshold.result())
        print("  ","Noise Level\t",diagnostics.result()["NoiseLevel"])
        print("  ","Signal Level\t",diagnostics.result()["signalLevel"])
        print("  ","Signal Margin\t",diagnostics.result()["signalMargin"])

    async def __issue_request(self, path):
        """ Helper function to execute a Web CLI command and return its response """
        # req = requests.get(self.base_url + path, auth=(self.user, self.password))
        async with self._session.get(self.base_url+path) as resp:
            # todo: look for errors from the response and throw and error here
            assert resp.status == 200
            responseJson = await resp.json()
            return responseJson[0]['RESPONSE']['pages']

    async def close(self):
        await self._session.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())