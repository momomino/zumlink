import asyncio
from zumlink import Radio, DataRate

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




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())