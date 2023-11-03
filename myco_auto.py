import datetime
import queue
import random
import re
import string
import threading
import time
import urllib.request
from random import randint

import names
import requests

import ssl

import undetected_chromedriver as uc
import multiprocessing as mp

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

from fake_useragent import UserAgent

ssl._create_default_https_context = ssl._create_unverified_context

# api key for ImprovMX
API_KEY = {
    'Authorization': 'Basic sk_34ed0aedf316409d83b45558e759b3b6'
}

EMAIL_ALIAS = "yunlei.cyou"
#EMAIL_ALIAS = "tkformenssr.top"
# video_queue = queue.Queue()

with open("video_url.txt", "r") as f:
    video_urls = f.read().split("\n")


class Worker(mp.Process):

    def __init__(self, name=None, queue=mp.Queue(), stop_ev=mp.Event(), daemon=True):
        self.queue = queue
        self.driver = None
        self.stop_ev = stop_ev
        if name is None:
            self.__class__.n += 1
            name = f'worker-{self.__class__.n}'
        super().__init__(name=name, daemon=daemon)

    def run(self):
        # self.driver = uc.Chrome(user_multi_procs=True)
        # while True:
        #     try:
        #         job = self.queue.get_nowait()
        #     except Empty:
        #         time.sleep(.1)
        #         continue
        #     if not job or not job.get('action'):
        #         break
        #     try:
        #         self.driver.get(job['url'])
        #         print('loaded ', job['url'], 'completely')
        #     except Exception as e:
        #         print(e)
        #
        #     print(self.name, 'loading ', job.get('url'))
        myco_run()

    def start(self) -> None:
        super().start()


def get_urls(video_q):
    global video_urls
    for v in video_urls:
        video_q.put(v)


def get_verification_url(mail_alias, domains, api_key):
    adder = "https://api.improvmx.com/v3/domains/" + domains + "/logs/" + mail_alias
    print(f'fetching new mail for {mail_alias}@{domains}...')
    while True:
        # print(f'fetching new mail for {mail_alias}@{domains}...')
        get_eml = requests.get(adder, headers=api_key).json()
        for url in get_eml['logs']:
            if "token" in url['url']:
                get_eml_code = urllib.request.urlopen(url['url'])
                code_html = get_eml_code.read()
                url = re.compile(r'(?<=<a href=3D")(.*?)(?=[\s">])').search(str(code_html)).group()
                clean_url = re.sub(r'=\\r\\n', '', url)
                clean_url = re.sub(r'upn=3D', 'upn=', clean_url)
                print('url got!')
                return clean_url
        if 'http' not in str(get_eml['logs']):
            time.sleep(1)


def gen_pwd():
    # =======================================#
    #   pwd at least one upper case letter   #
    # =======================================#

    # Define the length of the password
    password_length = random.randint(8, 20)

    # Define the possible characters that can be in the password
    letters = string.ascii_letters
    digits = string.digits
    special_chars = ''.join(char for char in string.punctuation if char not in "|&^.\"")
    possible_characters = letters + digits + special_chars

    # Ensure that the password contains at least one letter, one digit, and one special character
    password = [random.choice(letters), random.choice(digits), random.choice(special_chars)]

    # Generate the remaining characters for the password
    for i in range(password_length - 3):
        password.append(random.choice(possible_characters))

    # Shuffle the password characters and convert to a string
    random.shuffle(password)
    password = ''.join(password)

    return password


def check_login(wait):
    try:
        is_need_logged_in = \
            wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='btn-signin']")))
    except:
        is_need_logged_in = False

    return is_need_logged_in


def myco_run(username: str = None, pwd: str = None, video_queue: queue.Queue = None):
    try:
        # Set the Chrome WebDriver options
        options = uc.ChromeOptions()
#        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')

        userAgent = UserAgent(os='windows').random
        #options.add_argument(f"--user-agent={userAgent}")
        
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31'
        options.add_argument(f"--user-agent={ua}")

        options.headless = False
        driver = uc.Chrome(options=options) #, user_multi_procs=True)

#        chrome_options = webdriver.ChromeOptions()
#        chrome_options.add_argument('--no-sandbox')
#        chrome_options.add_argument('--headless')
#        chrome_options.add_argument('--disable-gpu')
#        chrome_options.add_argument('--disable-dev-shm-usage')

#        driver = webdriver.Chrome(options=chrome_options)
        
        # go to myco.io
        driver.get("https://myco.io/")
        
        # Get the User Agent string
        user_agent = driver.execute_script("return navigator.userAgent")
        
        #ua = UserAgent(os='windwos')

        # Print the User Agent
        print("User Agent:", user_agent)

        #time.sleep(3000)

        # set the waiter
        wait = WebDriverWait(driver, 30)

        # check if need register
        if username is None or pwd is None:
            # put video urls into queue for later use
            video_queue = queue.Queue()
            get_urls(video_queue)

            # click on Sign In
            signin_btn = driver.find_element(By.XPATH, '//button[@data-testid="btn-signin"]')
            wait.until(EC.visibility_of(signin_btn))
            signin_btn.click()

            # click on Sign Up Now
            register_btn = driver.find_element(By.XPATH, '//span[@data-testid="go-to-register"]')
            wait.until(EC.visibility_of(register_btn))
            register_btn.click()

            # generate an email address under domain name
            first_name = names.get_first_name()
            last_name = names.get_last_name()
            rand_num = randint(100000, 999999)
            username = f"{first_name}{last_name}{rand_num}"
            email_alias = f"{first_name}.{last_name}{rand_num}"
            email = f"{email_alias}@{EMAIL_ALIAS}"

            # generate a password for signup
            #pwd = gen_pwd()
            pwd = 'Test2345!'

            # write account into file
            # TODO

            # fill in the info for signup
            input_first_name = driver.find_element(By.XPATH, '//input[@data-testid="firstName"]')
            input_first_name.click()
            input_first_name.send_keys(first_name)

            input_last_name = driver.find_element(By.XPATH, '//input[@data-testid="lastName"]')
            input_last_name.click()
            input_last_name.send_keys(last_name)

            input_email = driver.find_element(By.XPATH, '//input[@data-testid="email"]')
            input_email.click()
            input_email.send_keys(email)

            input_user_name = driver.find_element(By.XPATH, '//input[@data-testid="userName"]')
            input_user_name.click()
            input_user_name.send_keys(username)

            input_pwd = driver.find_element(By.XPATH, '//input[@data-testid="password"]')
            input_pwd.click()
            input_pwd.send_keys(pwd)

            input_pwd_confirm = driver.find_element(By.XPATH, '//input[@data-testid="confirmPassword"]')
            input_pwd_confirm.click()
            input_pwd_confirm.send_keys(pwd)

            cts_check = driver.find_element(By.XPATH, '//input[@data-testid="tAndCCheckbox"]')
            cts_check.click()

            register_btn = driver.find_element(By.XPATH, '//button[@data-testid="register-btn"]')
            register_btn.click()

            # get verification url
            url = get_verification_url(str.lower(email_alias), EMAIL_ALIAS, API_KEY)
            # TODO: add timeout

            # open the url in a new tab
            # driver.execute_script("window.open()")
            # driver.switch_to.window(driver.window_handles[-1])
            driver.get(url)
            time.sleep(5)
            # driver.switch_to.window()
            # driver.execute_script("window.close()")

            # page refresh
            # driver.refresh()

            # go back to myco.io
            driver.get("https://myco.io/")

        #while True:
        # for every video, close the driver, release memory, and signin again to continue
        # Sign In
        signin_btn = driver.find_element(By.XPATH, '//button[@data-testid="btn-signin"]')
        wait.until(EC.visibility_of(signin_btn))
        signin_btn.click()

##            username = 'wudideren'
##            pwd = 'Test2345!'

        user_name_input = driver.find_element(By.XPATH, '//input[@data-testid="input-username"]')
        user_name_input.send_keys(username)
        pwd_input = driver.find_element(By.XPATH, '//input[@data-testid="input-password"]')
        pwd_input.send_keys(pwd)

        login_btn = driver.find_element(By.XPATH, '//button[@data-testid="login-SignIn"]')
        login_btn.click()

        # wait for signed-in page to load
        wait.until(EC.presence_of_element_located((By.XPATH, '//span[@data-testid="menu-item-logout"]')))

        retry = 0
        surfing_start_time = datetime.datetime.now()
        finish_watching = False

        url = video_queue.get()

        while retry < 3:
            print(f'try the {retry + 1} time with url:{url}')
            try:
                # go to the target video
                driver.get(url)

                #print('sleeping 10s')

                #time.sleep(10)
                
                print('waiting for play')
                
                # press play
                wait.until(EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Play"]')))

                play_btn_id = driver.find_element(By.XPATH, '//button[@aria-label="Play"]').get_attribute(
                    "id")
                play_btn = driver.find_element(By.XPATH, f'//button[@id="{play_btn_id}"]')
                wait.until(EC.visibility_of(play_btn))
                play_btn.click()

                print('play!')

                while True:
                    try:
                        time.sleep(3)
                        is_pressed = play_btn.get_attribute("aria-pressed")
                        if is_pressed == "true":
                            break
                        else:
                            play_btn.click()
                    except:
                        play_btn.click()

##                    print('checking total time')

                # get the total video time in seconds
                total_time = "0"
                while total_time == "0" or total_time is None:
                    total_time = driver.find_element(By.XPATH, '//div[@aria-label="Video timeline"]').get_attribute(
                        "aria-valuemax")

                print(total_time)

                while not finish_watching:
                    time.sleep(60)

                    # save screenshot
##                        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
##                        screenshot_filename = f'screenshot_{current_time}.png'
##                        driver.save_screenshot(screenshot_filename)

                    xpath = "//*[contains(text(), 'You are seeing an ad now')]"

                    ads_banner = driver.find_elements(By.XPATH, xpath)

                    if len(ads_banner) > 0:
#                            print('ads')
                        
##                            try:
##                                #skip_ad_button = driver.find_element(By.XPATH, '//button[@data-ck-tag="skip"]')
##                                skip_ad_buttn = driver.find_element_by_class_name('videoAdUiSkipButton videoAdUiAction videoAdUiRedesignedSkipButton')
##                                wait.until(EC.visibility_of(skip_ad_buttn))
##                                skip_ad_buttn.click()
##                                #print("Element exists")
##                            except NoSuchElementException:
##                                print("Skip btn does not exist")

##                            print('finding iframes')

                        # Find all iframes on the page
                        iframes = driver.find_elements(By.TAG_NAME, 'iframe')

##                            print('iterateing iframes')

                        # Iterate through each iframe and search for the element
                        for iframe in iframes:
                            try:
                                driver.switch_to.frame(iframe)  # Switch to the iframe
                            
                                element = driver.find_element(By.XPATH, '//button[@data-ck-tag="skip"]')  # Search for the element within the iframe

                                print('skip btn found')

                                # Perform actions with the found element
                                element.click()
                                
                                break  # If element found, break out of the loop
##                                except StaleElementReferenceException:
##                                    pass  # Stale element, continue to the next iframe
##                                except NoSuchElementException:
##                                    pass  # Element not found in this iframe, continue to the next
                            except:
                                pass


##                            print('switching back to default')
                        
                        # Switch back to the main page (outside of any iframes)
                        driver.switch_to.default_content()

##                            print('switched back')

                    #timeline = driver.find_element(By.XPATH, '//div[@aria-label="Video timeline"]')

                    #playtime = timeline.get_attribute("aria-valuenow")

                    #print(play_btn.get_attribute("aria-pressed"))

                    # update surfing time flag
                    surfing_time = (datetime.datetime.now() - surfing_start_time).total_seconds()
                    finish_watching = (surfing_time >= float(3060))
                break
            except TimeoutException:
                print('Time Out!')
                retry = retry + 1
                continue

            except Exception as e:
                print(f'retry err: {e}')

                # save screenshot
                current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                screenshot_filename = f'screenshot_watch_execption_{current_time}.png'
                driver.save_screenshot(screenshot_filename)
                    
                retry = retry + 1
                continue

        # logout
        logout_btn = driver.find_element(By.XPATH, '//span[@data-testid="menu-item-logout"]')
        logout_btn.click()

        time.sleep(5)

        # close driver
        driver.quit()

        time.sleep(5)

        if not video_queue.empty():
            # move to the next video
            myco_run(username, pwd, video_queue)

            #break

        # print('myco_run exit.')
    except Exception as e:
        try:
            print(f'myco_run() error: {e}')

            # close browser
            driver.quit()

            if not video_queue.empty():
                print('move to next video.')
                
                # move to the next video
                myco_run(username, pwd, video_queue)          
        except:
            pass


if __name__ == '__main__':
    # threads = []
    # for i in range(2):
    #     threads.append(threading.Thread(target=myco_run))
    #     threads[i].start()
    #     time.sleep(15)

    workers = [Worker(name=f'worker-{n}') for n in range(1)]

    for w in workers:
        w.start()
        time.sleep(60)

    for w in workers:
        w.join()

    # when thread died, create new threads to maintain 5-threads-pool
    # release the memory periodically
