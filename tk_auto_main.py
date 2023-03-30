import json
import random
import re
import threading
import time
from random import randint, uniform

import psutil as psutil
import requests
from playwright import sync_api
from playwright.sync_api import expect, sync_playwright
import datetime

from colors import bcolors

SURFING_PERIOD = 30


def timestamp():
    global date_fmt
    date_fmt = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    return bcolors.OKGREEN + f'[{date_fmt}]' + bcolors.OKCYAN + f' | {str(psutil.cpu_percent(1))} | '


def get_browser_context(port):
    playwright = sync_api.sync_playwright().start()
    browser = playwright.chromium.connect_over_cdp("http://127.0.0.1:" + str(port))
    context = browser.contexts[0]
    return context


def open_tiktok(browser_context_, is_headless):
    if is_headless:
        # 设定登入 cookies
        with open('[tiktok cookies]dr_for_men_.json', 'r') as f:
            cookies = json.load(f)
        # 修改 sameSite 值
        for cookie in cookies:
            if cookie["sameSite"] == "no_restriction":
                cookie["sameSite"] = "None"
            else:
                cookie["sameSite"] = "Lax"

        browser_context_.add_cookies(cookies)

    # 使用第一个标签页打开 TikTok.com
    page = browser_context_.pages[0]
    page.goto("https://www.tiktok.com")

    """
    idx = 0
    while True:
        idx = idx + 1
    """

    # interacting with the browser's Java API
    # memory = page.evaluate("performance.memory")

    # time.sleep(10)

    # 滑动视频
    # page.mouse.wheel(horizontally, vertically(positive is
    # scrolling down, negative is scrolling up)
    """
    for i in range(5):  # make the range as long as needed
        page.mouse.wheel(0, 1500)
        time.sleep(5)
        i += 1

    time.sleep(15)
    # ---------------------
    """

    # 首页搜索框搜寻 #减肥
    search_input = page.locator('//input[@name="q" and @data-e2e="search-user-input"]')
    search_input.fill('#amazon')
    search_btn = page.locator('//button[@type="submit" and @data-e2e="search-button"]')
    search_btn.click()

    # 先等搜索结果页面载入
    locator = page.locator('//div[@class="tiktok-yz6ijl-DivWrapper e1cg0wnj1"]/a')
    # page.wait_for_selector('div[class="tiktok-yz6ijl-DivWrapper e1cg0wnj1"]', timeout=10000)
    expect(locator.first).to_be_visible(timeout=10000)
    # print("waiting for the search to load...10s")
    # print(locator.count())

    i = 0
    while i < locator.count():
        while i < locator.count():

            # 随机决定是否看此视频
            watch = randint(1, 2)  # 1:watch; 2:not watch
            print(f'count:{i}, watch:{watch}')

            if watch == 2:
                i = i + 1
                continue

            # 随机决定完播比例
            completion_perc = 5.0  # uniform(70, 100)
            # print(f'completion: {completion_perc}%')

            # 点击视频观看
            locator.nth(i).click()

            # 等待视频完播
            while True:
                # 如果视频没有自动播放,则手动播放
                vid_player = page.locator('//*[contains(@class, "xgplayer")]')
                class_attr = vid_player.get_attribute('class')
                if "xgplayer-pause" in class_attr:
                    # 按空白键播放
                    page.keyboard.press(" ")

                # 获得已播放时间百分比%
                left = page.locator('//div[@class="tiktok-1ioucls-DivSeekBarCircle e1rpry1m4"]') \
                    .get_attribute("style")

                # 已播放时间百分比格式: style="left: calc(18.8044%);"
                perc = float(re.split(r"[(%);]", str(left))[1])
                # print(perc)
                if perc >= completion_perc:
                    print('finish watching')

                    """
                    # 点赞
                    like_btn = page.locator('//span[@data-e2e="browse-like-icon"]')
                    like_btn.click()
                    time.sleep(2)

                    # 评论
                    # 取得评论框
                    comment_box = page.locator('//div[@class="public-DraftEditorPlaceholder-root"]')

                    # 鼠标点击focus
                    comment_box.click()
                    time.sleep(3)

                    # 输入评论文字
                    page.keyboard.insert_text("so nice :)")
                    time.sleep(2)

                    # 取得发布按钮（评论框输入文字后，发布按钮才会Enable)
                    comment_post_btn = page.locator('//div[@data-e2e="comment-post"]')
                    expect(comment_post_btn).to_be_enabled()

                    # 发布
                    comment_post_btn.click()
                    time.sleep(3)

                    # 收藏
                    # 目前网页版没有收藏功能

                    # 转发
                    # TODO: 转发
                    """
                    break

            # 关闭video
            close_btn = page.locator('//button[@data-e2e="browse-close"]')
            close_btn.click()
            time.sleep(2)

            i = i + 1

        # 拉到最底部
        # page.keyboard.press('End')

        # 判断”Load more“按钮是否存在
        is_btn_exist = page.wait_for_selector("button[data-e2e='search-load-more']", timeout=10000)
        if is_btn_exist:
            # 载入更多视频
            load_more_btn = page.locator('//button[@data-e2e="search-load-more"]')
            load_more_btn.click()
        else:
            # 刷到底了，没有更多视频了
            print("[keyword search] finished")
            break

        # 更新locator
        locator = page.locator('//div[@class="tiktok-yz6ijl-DivWrapper e1cg0wnj1"]/a')
        # page.wait_for_selector('div[class="tiktok-yz6ijl-DivWrapper e1cg0wnj1"]', timeout=10000)
        expect(locator.nth(i)).to_be_visible(timeout=10000)

    # page.close()

    # TODO: 所有requests、playwright 等使用第三方服務的地方，都要加入 try-catch 来处理未知错误：重新整理，跑下一个账号
    # TODO: 动态释放 memory，不然浏览器会 crash


def tiktok_foryou(browser_context_, container_name):  # , is_headless):
    # """
    # if is_headless:
    #     # 设定登入 cookies
    #     with open('[tiktok cookies]dr_for_men_.json', 'r') as f:
    #         cookies = json.load(f)
    #     # 修改 sameSite 值
    #     for cookie in cookies:
    #         if cookie["sameSite"] == "no_restriction":
    #             cookie["sameSite"] = "None"
    #         else:
    #             cookie["sameSite"] = "Lax"
    #
    #     browser_context_.add_cookies(cookies)
    # """

    # 使用第一个标签页打开 TikTok.com

    page = browser_context_.pages[0]
    page.goto("https://www.tiktok.com")
    # page.evaluate('document.body.style.zoom = "80%"')

    # 滑动视频
    # page.mouse.wheel(horizontally, vertically(positive is
    # scrolling down, negative is scrolling up)
    """
    for i in range(5):  # make the range as long as needed
        page.mouse.wheel(0, 1500)
        time.sleep(5)
        i += 1

    time.sleep(15)
    # ---------------------
    """
    # idx = 1

    finish_surfing = False
    surfing_start_time = datetime.datetime.now()  # get_current_time_min()

    while not finish_surfing:
        # random foryou count
        update_foryou_count = randint(5, 20)  # number of videos to watch before reload the foryou page

        # 首页第一个视频
        videos_foryou = page.locator('//div[@class="tiktok-1631c5i-DivVideoCardContainer e1bh0wg77"]')
        expect(videos_foryou.first).to_be_visible(timeout=10000)

        # 先点开，进入大屏播放页面
        videos_foryou.nth(0).click()

        idx = 1
        while not finish_surfing:
            # 随机决定完播比例
            completion_perc = uniform(20, 80)
            # print(f'completion: {completion_perc}%')

            # wait for the video completion
            # format: mm:ss/mm:ss
            video_time_container = \
                page.locator('//div[@class="tiktok-o2z5xv-DivSeekBarTimeContainer e1rpry1m1"]').text_content()

            # t1, t2 format: mm, ss
            t1, t2 = video_time_container.split('/')

            # format: hh:mm
            m, s = t2.split(':')
            video_sec = int(m) * 60 + int(s)

            # wait for the video playing
            time_to_sleep = int(video_sec * completion_perc * 0.01)

            # need to split 'time_to_sleep' into 3 parts:
            # Before Like
            # Like-to-Comment
            # Comment-to-end

            # calculate time_to_sleep sections
            # time.sleep(time_to_sleep)
            t1, t2, t3 = split_time(container_name, time_to_sleep)

            # sleep before Like
            threading.Event().wait(t1)

            # print(f'count:{idx}, finish watching.')

            need_login = (page.locator("//*[contains(text(), 'Log in to comment')]").count() == 2)

            # Like
            if (not need_login) and random.choice([True, False]):
                like_btn = page.locator('//span[@data-e2e="browse-like-icon"]')
                like_btn.click()
                # print('Like!')
                time.sleep(2)
            else:
                pass
                # print('not Like.')

            # TODO: 一次 sleep 太长时间，容易卡死，可以分多次小的 sleep 跑 loop

            # sleep before Comment
            threading.Event().wait(t2)

            # Comment

            # print(f'need_login:{need_login}')
            if (not need_login) and random.choice([True, False]):
                # get the comment box
                comment_box = page.locator('//div[@class="public-DraftEditorPlaceholder-root"]')

                # mouse click to focus
                comment_box.click()
                time.sleep(3)

                # keyboard input
                # constantly scraping comments from other's posts and write into local file (AI assisted)
                # read from local file into a global queue
                page.keyboard.insert_text("so nice :)")
                time.sleep(2)

                # get the post button (评论框输入文字后，发布按钮才会Enable)
                comment_post_btn = page.locator('//div[@data-e2e="comment-post"]')
                expect(comment_post_btn).to_be_enabled()

                # post
                comment_post_btn.click()
                # print('Comment!')
                time.sleep(3)
            else:
                pass
                # print('no comment.')

            # Favorite
            # 目前网页版没有收藏功能

            # share
            # TODO: share

            # sleep before finish video
            threading.Event().wait(t3)

            idx = idx + 1

            # update surfing time flag
            surfing_now_time = datetime.datetime.now()  # get_current_time_min()
            surfing_time = (surfing_now_time - surfing_start_time).total_seconds()
            print(timestamp() + f'[{container_name}]surfing_time(sec):{int(surfing_time)}')
            finish_surfing = (surfing_time >= SURFING_PERIOD * 60)

            # 如果已经刷超过x条视频，则跳出loop刷新for you推荐列表
            if idx > update_foryou_count:
                # 关闭video页面
                close_btn = page.locator('//button[@data-e2e="browse-close"]')
                close_btn.click()
                time.sleep(2)
                # 点击 For You 按钮，刷新推荐列表
                for_you_btn = page.locator('//a[@data-e2e="nav-foryou"]')
                for_you_btn.click()
                time.sleep(2)
                break

            # 判断”向下“按钮是否存在
            is_btn_exist = page.wait_for_selector("button[data-e2e='arrow-right']", timeout=10000)
            if is_btn_exist:
                # 载入更多视频
                next_vid_btn = page.locator('//button[@data-e2e="arrow-right"]')
                next_vid_btn.click()
            else:
                # 刷到底了，没有更多视频了
                print("[keyword search] finished")
                finish_surfing = True
                break

    # close video browsing page
    close_btn = page.locator('//button[@data-e2e="browse-close"]')
    close_btn.click()
    time.sleep(2)
    page.close()

    print(f'[{container_name}] finish surfing, closing now...')

    # TODO: 所有requests、playwright 等使用第三方服務的地方，都要加入 try-catch 来处理未知错误：重新整理，跑下一个账号
    # TODO: periodically close tab to release memory


def start_browser_and_go(env_data):  # , is_headless):
    # data = {}  # dict
    # while True:
    try:
        print(f"starting browser...code: {env_data['containerCode']}")
        result = requests.post(f"http://127.0.0.1:6873/api/v1/browser/start",
                               json={'containerCode': f"{env_data['containerCode']}", 'args': ["--start-maximized"]}).json()

        if 'Success' in result['msg']:
            debuggingPort = result['data']['debuggingPort']
            # break
        else:
            exit()
    except:
        exit()
        pass

    # except Exception as e:
    # TODO: add retry (3 times)
    # print(f'[startup]something went wrong: {e}')
    # if data != {}:
    #     result = requests.get(f"http://127.0.0.1:6873/api/v1/browser/stop", params=data).json()
    #     print("close browser:" + str(jsonpath(result, '$..msg')))
    # exit()

    # get playwright browser handler
    browser_context = get_browser_context(debuggingPort)  # fill in 'debuggingPort'

    # """
    # run script
    try:
        # open_tiktok(browser_context, data['isHeadless'])
        tiktok_foryou(browser_context, env_data['containerName'])  # , data['isHeadless'])
        # tiktok_create_account(browser_context)
    except Exception as e:
        print(f'[open TikTok]something went wrong: {e}')
        result = requests.get(f"http://127.0.0.1:6873/api/v1/browser/stop",
                              params={'containerCode': f"{env_data['containerCode']}"}).json()

        print("close browser:" + result['msg'])
        print('starting another account...')

    # starting another account
    # """


def split_time(container_name, original_value):
    # Generate two random integers between 0 and the original value
    rand1 = random.uniform(original_value / 2, original_value)

    rand2 = random.uniform(0, original_value - rand1)

    # Calculate the third integer such that their sum equals the original value
    rand3 = original_value - rand1 - rand2

    # Print the results
    print(timestamp() + f'[{container_name}]{rand1}, {rand2}, {rand3}       | {rand1 + rand2 + rand3}')

    return rand1, rand2, rand3


if __name__ == '__main__':
    # for _ in range(1000):
    #     split_time(45.3)
    #
    # exit()

    date_fmt = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    #
    # # get cpu usage %
    cpu_usage = str(psutil.cpu_percent(1))
    #
    # for _ in range(70):
    #     cpu = str(psutil.cpu_percent(0.2))
    #     cpu_usage = cpu + '%' + ' ' * (5 - len(cpu)) if cpu != '0.0' else cpu_usage
    #     print(cpu_usage)
    #
    # print(timestamp())

    # threads = 5
    # position = 2
    #
    # factor = int(threads / (0.1 * threads + 1))
    # sleep_time = int((str(position)[-1])) * factor
    # print(f'sleep_time: {sleep_time}')

    # exit()

    try:
        # get environment lists
        res = requests.post(f"http://127.0.0.1:6873/api/v1/env/list").json()
        env_list = res['data']['list']

        """
        # create environment
        data_for_create = {
            'containerName': "google-us-2-test",
            'asDynamicType': 1,
            'proxyTypeName': "不使用代理",
            'ua': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }

        res = requests.post(f"http://127.0.0.1:6873/api/v1/env/create", json=data_for_create).json()
        print(res)

        # update environment
        data_for_update = {
            'containerCode': container_code_list[3],
            'containerName': container_name_list[3],
            'ua': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }
        #res = requests.post(f"http://127.0.0.1:6873/api/v1/env/update", json=data_for_update).json()

        #print(res)
        """
    except Exception as e:
        print(f'[startup]something went wrong: {e}')
        exit()

    # create threads with args
    threads = []
    for i in range(1):
        threads.append(threading.Thread(target=start_browser_and_go, args=(env_list[1],)))
        threads[i].start()
