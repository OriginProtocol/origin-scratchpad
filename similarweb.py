#! Python3
"""
    File name: treasuries.py
    Author: Jonathan Snow
    Date created: 10/21/2022
    Python Version: 3.9.x
    File Details:
        Purpose: A series of functions to pull traffic data from
        similarweb for a list of URLs.
        - Need to create a free trial account on similarweb
        - CSS Class could change

"""

# Imports
from modules import data
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By

URL = "https://pro.similarweb.com/#/digitalsuite/websiteanalysis/overview/website-performance/*/999/1m?webSource=Total&key={}"

# WEBDRIVER SETUP
OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument("--start-maximized")
OPTIONS.add_argument("--disable-infobars")
OPTIONS.add_argument("--window-size=2000,3000")
driver = webdriver.Chrome(options=OPTIONS)

STATS_CLASS = "MetricValue-edQheR"
APP_CLASS = "a.AppIconLink-OjIKx"


##################################################
def main():
    """
    Function to gather treasury addresses from Cryptostats.
    """
    output = []

    # List of all websites to process
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

    # Login to website
    login()
    
    # Loop through websites in list
    for url in websites:
        result = process(url)
        output.append(result)


    # Dump balance data to CSV
    output_path = "files/output"
    output_name = "sw_sites-1.csv"
    data.save(output, output_path, output_name, ["url", "traffic", "users", "ios_id", "android_id"])


##############################################################
def login():
    """
    Function to log in to similarweb.com
    """
    driver.get(URL)
    sleep(45) # Allow 30s to log into application


##############################################################
def process(website):
    """
    Function to process a website on similarweb.com
    """
    app_ios = []
    app_android = []
    driver.get(URL.format(website))
    sleep(5)
    elements = driver.find_elements(By.CLASS_NAME, STATS_CLASS)

    # Grab relevant traffic and user data from page
    traffic = elements[0].text
    users = elements[1].text
    print(website, ", ", traffic, ", ", users)
    
    # Grab relevant app data links
    app_elements = driver.find_elements(By.CSS_SELECTOR, APP_CLASS)

    # Loop over apps listed and extract app ID codes
    if len(app_elements) > 0:
        for app in app_elements:
            link = app.get_attribute('href').replace("https://pro.similarweb.com/#/apps/performance/", "").split("/")[0]
            print(link)

            # Sort link by App Store
            if "1_" in link:
                app_ios.append(link.replace("1_",""))
            elif "0_" in link:
                app_android.append(link.replace("0_",""))

    sleep(10)
    return [website, traffic, users, app_ios, app_android]


##################################################
# Runtime Entry Point
if __name__ == "__main__":
    main()
