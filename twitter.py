#! Python3
"""
    File name: twitter.py
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to search for Twitter
        handles on provided websites, and return the handle
        and the current number of followers.

"""

from modules import data
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By

# WEBDRIVER SETUP
OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument("--start-maximized")
OPTIONS.add_argument("--disable-infobars")
OPTIONS.add_argument("--window-size=2000,3000")
driver = webdriver.Chrome(options=OPTIONS)


##################################################
def main():
    output = []
    websites = [
        'rabby.io',
        'tally.cash',
        'bitkeep.com',
        'www.ledger.com',
        'etherscan.io',
        'ethereum.org',
        'www.sushi.com',
        'balancer.fi',
        'lunarcrush.com',
        'walleth.org',
        'mooniswap.exchange',
        'www.defipulse.com',
        'www.dapp.com',
        'dappradar.com',
        'www.tokensets.com',
        'vemarketcap.com',
        'sablier.finance',
        'kyberswap.com',
        'www.exodus.com',
        'www.numio.one',
        'www.safepal.com',
        'www.ellipal.com',
        'www.coinomi.com',
        'www.pillar.fi',
        'www.nansen.ai',
        'defisaver.com',
        'paxos.com',
        'tangany.com',
        'www.vauld.com',
        'tokenlists.org',
        'xangle.io',
        'hextrust.com',
        'home.bancor.network',
        'www.venly.io',
        'liquidswap.com',
        'frame.sh',
        'transak.com',
        'www.frontier.xyz',
        'www.matcha.xyz',
        'fortmatic.com',
        'wallet.polygon.technology',
        'www.etherwall.com',
        'www.parity.io',
        'alphawallet.com',
        'freewallet.org',
        'www.balance.io',
        'www.amberdata.io',
        'ann.hoo.comannouncement',
        'myabcwallet.io',
        'airgap.io',
        'bitpie.com',
        'blockmove.io',
        'www.buntoy.com',
        'cobo.com',
        'www.cryptonator.com',
        'cryptopay.me',
        'www.dexwallet.io',
        'btxpro.com',
        'etherscan.io',
        'www.hel.io',
        'hut34.io',
        'www.infinitowallet.io',
        'particl.io',
        'phenom-elon.com',
        'ww25.qbao.fund',
        'mysafewallet.io',
        'diversifi.app',
        'monarchwallet.com',
        'midasprotocol.io',
        'monolith.xyz',
        'gocrypto.com',
        'block.cc',
        'www.atoken.com',
        'unocoin.com',
        'klever.io',
        'www.birdchainapp.com',
        'blockstream.com',
        'totalcoin.io',
        'tenx.tech',
        'www.hb-wallet.com',
        'www.socios.com',
        'natrium.io',
        'quppy.com',
        'litecoin.org',
        'coindirect.com',
        'www.coinspot.com.au',
        'cash.app',
        'bitcoin.com',
        'lobstr.co',
        'www.coinpayments.net',
        'www.maicoin.com',
        'www.wombat.app',
        'www.tronlink.org',
        'electrum.org',
        'choise.com',
        'spectrocoin.com',
        'swipe.io',
        'www.jstcap.com',
        'www.xdefi.io',
        'www.airswap.io',
        'www.altonomy.com',
        'dydx.exchange',
        'peakdefi.com',
        'staker.app',
        'o3.network',
        'unstoppable.money',
        'synthetix.io',
        'wazirx.com',
        'www.cypherwallet.io',
        'www.coinzoom.com',
        'linen.app',
        'multis.com',
        'walleth.org',
        'www.sktelecom.com',
        'keys.casa',
        'www.ethvm.com',
        'mewconnect.myetherwallet.com',
        'elasticswap.org',
        'teleport.network',
        'www.enkrypt.com',
        'www.minke.app',
        'hyve.works',
        'arcticwallet.io',
        'omni.app',
        'www.hyperpay.tech',
        'defiantapp.tech',
        'www.zulutransfer.com',
        'exponential.fi',
        'walletnow.app',
        'changehero.io',
        'exolix.com',
        'letsexchange.io',
        'godex.io',
        'sideshift.ai',
        'www.switchain.com',
        'thegivingblock.com',
        'cryptowallet.com',
        'burritowallet.com'
    ]
    
    for url in websites:
        handle = process(url)
        followers = get_followers(handle)
        output.append([url, handle, followers])


    # Dump balance data to CSV
    output_path = "files/output"
    output_name = "sw_twitter-2.csv"
    data.save(output, output_path, output_name, ["url", "handle", "followers"])


##############################################################
def process(website):
    """
    Function to process a website and search for Twitter links
    """

    try:
        driver.get("https://" + website)
    except Exception as e:
        print(e)
        return "N/A"

    sleep(2)
    elements = driver.find_elements(By.TAG_NAME, "a")

    for element in elements:
        link = element.get_attribute("href")
        if link is not None and "twitter.com" in link and "status" not in link:
            handle = clean(link)
            print("Handle Found: " + handle)
            return handle

    return "N/A"


##############################################################
def clean(link):
    """
    Function to clean up a Twitter handle
    """
    handle = link.replace("https://twitter.com/","")
    handle = handle.replace("https://www.twitter.com/","")

    return handle


##############################################################
def get_followers(handle):
    """
    Function to clean up a Twitter handle
    """

    if "N/A" in handle: return "N/A"

    driver.get("https://twitter.com/" + handle)
    sleep(4)

    elements = driver.find_elements(By.TAG_NAME, "a")

    for element in elements:
        link = element.get_attribute("href")

        # Check for substring in link
        if link is not None and "/followers" in link:
            count = element.find_elements(By.TAG_NAME, "span")[0]
            print(handle + ": " + count.text)
            return(count.text)



##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
