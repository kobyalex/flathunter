"""Chrome needs some special handling to work out where the correct
binary is, to attach the correct selenium chromedriver, and to set
the correct version number"""
import re
import subprocess
from selenium import webdriver

from flathunter.logging import logger
from flathunter.exceptions import ChromeNotFound

CHROME_VERSION_REGEXP = re.compile(r'.* (\d+\.\d+\.\d+\.\d+)( .*)?')

def get_command_output(args):
    """Run a command and return the first line of stdout"""
    try:
        with subprocess.Popen(args,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True) as process:
            if process.stdout is None:
                return None
            return process.stdout.readline()
    except FileNotFoundError:
        return None

def get_chrome_version() -> tuple:
    """Determine the correct name for the chrome binary"""
    for binary_name in ['google-chrome', 'chromium', 'chrome', "chromedriver"]:
        try:
            version = get_command_output([binary_name, '--version'])
            if version is None:
                continue
            match = CHROME_VERSION_REGEXP.match(version)
            if match is None:
                continue
            return int(match.group(1).split('.')[0]), binary_name
        except FileNotFoundError:
            pass
    raise ChromeNotFound()

def get_chromedriver_path(binary_name: str) -> str:
    """Determine the correct path for the chrome driver binary"""
    chromedriver_path = get_command_output(['which', binary_name])
    if chromedriver_path is None:
        raise ChromeNotFound()
    return chromedriver_path.strip(" \n")


def get_chrome_driver(driver_arguments):
    """Configure Chrome WebDriver"""
    logger.info('Initializing Chrome WebDriver for crawler...')
    chrome_options = webdriver.ChromeOptions() # pylint: disable=no-member
    if driver_arguments is not None:
        for driver_argument in driver_arguments:
            chrome_options.add_argument(driver_argument)
    chrome_version, chrome_binary = get_chrome_version()
    chromedriver_path = get_chromedriver_path(chrome_binary)
    # driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options) # pylint: disable=no-member
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options) # pylint: disable=no-member

    driver.execute_cdp_cmd('Network.setBlockedURLs',
        {"urls": ["https://api.geetest.com/get.*"]})
    driver.execute_cdp_cmd('Network.enable', {})
    return driver


# import undetected_chromedriver as uc
# from undetected_chromedriver import ChromeOptions
# from undetected_chromedriver.utils import get_chrome_version

# def get_chrome_driver(driver_arguments):
#     """Configure Chrome WebDriver"""
#     print('Initializing Chrome WebDriver for crawler...')  # Use print for demonstration
#     chrome_options = ChromeOptions()
#     if driver_arguments is not None:
#         for driver_argument in driver_arguments:
#             chrome_options.add_argument(driver_argument)
#     chrome_version = get_chrome_version()
#     # Set the path to Chromedriver executable (replace with your actual path)
#     chromedriver_path = '/usr/bin/chromedriver'
#     options = uc.ChromeOptions()
#     options.add_argument('--disable-dev-shm-usage')  # Add any additional options here
#     # Create Chrome WebDriver with the specified Chromedriver path and options
#     driver = uc.Chrome(executable_path=chromedriver_path, chrome_options=options, version_main=chrome_version)
#     driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ["https://api.geetest.com/get.*"]})
#     driver.execute_cdp_cmd('Network.enable', {})
#     return driver