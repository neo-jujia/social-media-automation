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
from playwright import sync_api
from playwright.sync_api import expect

# api key for ImprovMX
API_KEY = {
    'Authorization': 'Basic sk_34ed0aedf316409d83b45558e759b3b6'
}

EMAIL_ALIAS = "yunlei.cyou"
# video_queue = queue.Queue()

with open("video_url.txt", "r") as f:
    video_urls = f.read().split("\n")
    # for v in video_urls:
    #     video_queue.put(v)


def get_browser_context(port):
    playwright = sync_api.sync_playwright().start()
    browser = playwright.chromium.connect_over_cdp("http://127.0.0.1:" + str(port))
    context = browser.contexts[0]
    return context


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


def create_env(ip_server, ip_port, ip_acc, ip_pass, container_name, remark_email, tag_name):
    datas = {
        'containerName': container_name,  # 环境名称
        'remark': remark_email,  # 备注
        'tagName': tag_name,  # 分组名称
        'asDynamicType': '2',  # ip选择 (1-静态 ，2-动态)
        'proxyTypeName': '不使用代理',  # HTTP HTTPS ip类型
        'proxyServer': ip_server,  # ip
        'proxyPort': ip_port,  # ip端口
        'proxyAccount': ip_acc,  # ip账号
        'proxyPassword': ip_pass,  # ip密码
        'type': 'windows',  # 操作系统 windows  android ios, 默认win
        'coreVersion': '105',  # 内核版本号 chromedriver判断
        'videoThrottle': '2',  # 视频限流 0关闭 1开启 2跟随团队。不传参默认跟随团队。
        'imgThrottle': '2',  # 图片限流 0关闭 1自定义 2跟随团队。不传参默认跟随团队
        "advancedBo": {'uaVersion': '105',  # 范围包括95、96、97、98、99、100、101、102、103、104、105、106。
                       'geoTips': '0',  # 0-ask（询问）、2-block（禁止
                       'geoRule': '0',  # 0-基于IP生成对应位置，1-使用自定义设置的位置
                       'fontFingerprint': '0',  # 0-开启ClientRects隐私保护，1-使用电脑默认的ClientRects
                       'webRtc': '0',
                       # 0-开启WebRTC，但禁止获取IP，1-开启WebRTC，将公网IP替换为代理IP，2-开启WebRTC，跟随电脑真实IP，3-禁用WebRTC，网站会检测到您关闭了WebRTC
                       'canvas': '0',  # 0-开启Canvas隐私保护，1-跟随电脑的Canvas
                       'webgL': '0',  # 0-开启WebGL隐私保护，1-跟随电脑的WebGL
                       'hardwareAcceleration': '1',  # 0-关闭硬件加速，1-开启硬件加速
                       'webglinfo': '0',  # 0-开启WebGL Info隐私保护，1-跟随电脑的WebGL Info，2-使用您设置的WebGL Info
                       'audioContext': '0',  # 0-开启AudioContext隐私保护，1-跟随电脑的AudioContext
                       'speechVoices': '0',  # 0-开启SpeechVoices，1-关闭SpeechVoicess
                       'media': '0',  # 0-开启媒体设备隐私保护，1-使用Chrome原生隐私保护（不授权则不会暴露真实媒体设备数量）
                       'doNotTrack': '1',  # 0-默认不设置，1-默认不允许追踪，2-默认允许追踪
                       'portScan': '0',  # 0-不允许网站检测您使用的本地网络端口，1-允许网站检测您使用的本地网络端口
                       }
    }
    print(f"thread_{threading.current_thread().ident}: creating browser environment...")
    idcode = requests.post(f"http://127.0.0.1:6873/api/v1/env/create", json=datas, timeout=60).json()

    return idcode


def get_web_port(ip_server, ip_port, ip_acc, ip_pass, container_name, remark_email, tag_name):
    while True:
        print(f"thread_{threading.current_thread().ident}: creating browser environment...")
        idcode = create_env(ip_server, ip_port, ip_acc, ip_pass, container_name, remark_email, tag_name)
        id = idcode['data']['containerCode']
        if 'Success' in idcode['msg']:
            while True:
                print(f"thread_{threading.current_thread().ident}: starting browser...")
                try:
                    debuggingPort = requests.post(f"http://127.0.0.1:6873/api/v1/browser/start",
                                                  json={
                                                      'containerCode': f"{id}"
                                                  }).json()

                    if 'Success' in debuggingPort['msg']:
                        doko = debuggingPort['data']['debuggingPort']
                        return id, doko
                except:
                    pass


def close_browser(container_code):
    res = requests.get(f"http://127.0.0.1:6873/api/v1/browser/stop", params={'containerCode': container_code}).json()
    return res


def delete_env(container_codes):
    res = requests.post(f"http://127.0.0.1:6873/api/v1/env/del", json={'containerCodes': container_codes},
                        timeout=60).json()
    if res['msg'] == 'Success':
        print('successfully delete environments.')
    else:
        print('[delete env] something went wrong.')


def myco_run():
    c_name = randint(100000, 9999999)

    # [hubstudio] create browser environment and start the browser
    container_code, debugging_port = get_web_port('', '', '', '', str(c_name), '', "myco_auto")

    # get browser context
    browser_context_ = get_browser_context(debugging_port)

    # go to myco.io
    page = browser_context_.pages[0]
    page.goto("https://myco.io/")

    # check if Logged in
    try:
        is_need_logged_in = page.wait_for_selector("button[data-testid='btn-signin']", timeout=10000)
    except:
        is_need_logged_in = False

    if is_need_logged_in:
        # click on Sign In
        signin_btn = page.locator('//button[@data-testid="btn-signin"]')
        expect(signin_btn).to_be_visible(timeout=10000)
        signin_btn.click()

        # click on Sign Up Now
        register_btn = page.locator('//span[@data-testid="go-to-register"]')
        expect(register_btn).to_be_visible(timeout=10000)
        register_btn.click()

        # generate an email address under domain name
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        rand_num = randint(100000, 999999)
        user_name = f"{first_name}{last_name}{rand_num}"
        email_alias = f"{first_name}.{last_name}{rand_num}"
        email = f"{email_alias}@{EMAIL_ALIAS}"

        # generate a password for signup
        password = gen_pwd()

        # write account into file
        # TODO

        # fill in the info for signup
        input_first_name = page.locator('//input[@data-testid="firstName"]')
        input_first_name.focus()
        input_first_name.fill(first_name)

        input_last_name = page.locator('//input[@data-testid="lastName"]')
        input_last_name.focus()
        input_last_name.fill(last_name)

        input_email = page.locator('//input[@data-testid="email"]')
        input_email.focus()
        input_email.fill(email)

        input_user_name = page.locator('//input[@data-testid="userName"]')
        input_user_name.focus()
        input_user_name.fill(user_name)

        input_pwd = page.locator('//input[@data-testid="password"]')
        input_pwd.focus()
        input_pwd.fill(password)

        input_pwd_confirm = page.locator('//input[@data-testid="confirmPassword"]')
        input_pwd_confirm.focus()
        input_pwd_confirm.fill(password)

        cts_check = page.locator('//input[@data-testid="tAndCCheckbox"]')
        cts_check.check()

        register_btn = page.locator('//button[@data-testid="register-btn"]')
        register_btn.click()

        # get verification url
        url = get_verification_url(str.lower(email_alias), EMAIL_ALIAS, API_KEY)

        # click the url
        page1 = browser_context_.new_page()
        page1.goto(url)
        time.sleep(5)
        page1.close()

        # page refresh
        page.reload()

        # Sign In
        signin_btn = page.locator('//button[@data-testid="btn-signin"]')
        expect(signin_btn).to_be_visible(timeout=10000)
        signin_btn.click()

        user_name_input = page.locator('//input[@data-testid="input-username"]')
        user_name_input.fill(user_name)
        pwd_input = page.locator('//input[@data-testid="input-password"]')
        pwd_input.fill(password)

        login_btn = page.locator('//button[@data-testid="login-SignIn"]')
        login_btn.click()

        # wait for page to load
        log_out_btn = page.locator('//span[@data-testid="menu-item-logout"]')
        expect(log_out_btn).to_be_visible(timeout=10000)

    global video_urls
    for url in video_urls:
        # for every 5 videos, close the page, release memory, and signin again to continue
        retry = 0
        while retry < 3:
            print(f'try the {retry + 1} time')
            try:
                # go to the target video
                page.goto(url)

                # press play
                play_btn_id = page.locator('//button[@aria-label="Play/Pause"]').get_attribute("id")
                play_btn = page.locator(f'//button[@id="{play_btn_id}"]')
                expect(play_btn).to_be_visible(timeout=10000)
                play_btn.click()

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

                # get the total video time in seconds
                total_time = "0"
                while total_time == "0" or total_time is None:
                    total_time = page.locator('//div[@aria-label="Video timeline"]').get_attribute("aria-valuemax")

                print(total_time)

                finish_watching = False
                surfing_start_time = datetime.datetime.now()

                while not finish_watching:
                    time.sleep(5)
                    #
                    # play_btn_id = page.locator('//button[@aria-label="Play/Pause"]').get_attribute("id")
                    # play_btn = page.locator(f'//button[@id="{play_btn_id}"]')
                    # is_pressed = play_btn.get_attribute("aria-pressed")
                    # if is_pressed == "false":
                    #     play_btn.click()

                    # update surfing time flag
                    surfing_time = (datetime.datetime.now() - surfing_start_time).total_seconds()
                    finish_watching = (surfing_time >= float(total_time))
                break
            except:
                retry = retry + 1
                continue

    time.sleep(2)
    page.close()

    # close browser
    close_browser(container_code)

    # delete env
    delete_env([container_code])


# def start_browser_and_go(env_data):
#     try:
#         print(f"starting browser...code: {env_data['containerCode']}")
#         result = requests.post(f"http://127.0.0.1:6873/api/v1/browser/start",
#                                json={'containerCode': f"{env_data['containerCode']}",
#                                      'args': ["--start-maximized"]}).json()
#
#         if 'Success' in result['msg']:
#             debuggingPort = result['data']['debuggingPort']
#             # break
#         else:
#             exit()
#     except:
#         exit()
#
#     browser_context = get_browser_context(debuggingPort)  # fill in 'debuggingPort'
#
#     # run script
#     try:
#         myco_run(browser_context, env_data['containerName'])  # , data['isHeadless'])
#     except Exception as e:
#         print(f'[open TikTok]something went wrong: {e}')
#         result = requests.get(f"http://127.0.0.1:6873/api/v1/browser/stop",
#                               params={'containerCode': f"{env_data['containerCode']}"}).json()
#
#         print("close browser:" + result['msg'])
#         print('starting another account...')


if __name__ == '__main__':
    # try:
    #     # get environment lists
    #     res = requests.post(f"http://127.0.0.1:6873/api/v1/env/list").json()
    #     env_list = res['data']['list']
    # except Exception as e:
    #     print(f'[startup]something went wrong: {e}')
    #     exit()

    threads = []
    for i in range(1):
        threads.append(threading.Thread(target=myco_run))
        threads[i].start()
        time.sleep(60)

    # release the memory periodically
