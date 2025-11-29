import time

import base64
from DrissionPage import ChromiumPage, ChromiumOptions


def run_bilibilishiping_js():
    """bilibili视频发布"""
    chrome_exe_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    co = ChromiumOptions()
    co.set_local_port(60741)
    co.set_browser_path(chrome_exe_path)
    page = ChromiumPage(addr_or_opts=co)
    page.get("https://member.bilibili.com/platform/upload/video/frame?page_from=creative_home_top_upload")
    # 登录后才能运行下面的发布代码
    time.sleep(10)
    with open("./jsscript/bilibilishiping.js", "r", encoding="utf-8") as r:
        zr = r.read()
    # 视频
    i = open(r"./output1.mp4", "rb")
    encoded_string = base64.b64encode(i.read()).decode('utf-8')
    # 标题
    title = "今天天气真好"
    zr = zr % (encoded_string, title)
    page.run_js(zr)


def run_bilibilituwen_js():
    """bilibili图文发布"""
    chrome_exe_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    co = ChromiumOptions()
    co.set_local_port(60741)
    co.set_browser_path(chrome_exe_path)
    page = ChromiumPage(addr_or_opts=co)
    page.get("https://member.bilibili.com/platform/upload/text/edit")
    # 登录后才能运行下面的发布代码
    time.sleep(10)
    with open("./jsscript/bilibilituwen.js", "r", encoding="utf-8") as r:
        zr = r.read()
    title = "今天天气真好"
    content = "生活中的美好往往就藏在这些看似平凡的瞬间"
    zr = zr % (title, content)
    page.run_js(zr)


def run_tenxunweishi_js():
    """腾讯微视视频发布"""
    chrome_exe_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    co = ChromiumOptions()
    co.set_local_port(60741)
    co.set_browser_path(chrome_exe_path)
    page = ChromiumPage(addr_or_opts=co)
    page.get("https://media.weishi.qq.com/")
    time.sleep(10)
    # 登录后才能运行下面的发布代码
    with open("./jsscript/tenxunweishi.js", "r", encoding="utf-8") as r:
        zr = r.read()
    # 视频
    video = open(r"./output1.mp4", "rb")
    video_encoded_string = base64.b64encode(video.read()).decode('utf-8')
    # 视频描述
    description = "今天天气真好"
    zr = zr % (video_encoded_string, description)
    page.run_js(zr)


def run_douyinshiping_js():
    """抖音视频发布"""
    chrome_exe_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    co = ChromiumOptions()
    co.set_local_port(60741)
    co.set_browser_path(chrome_exe_path)
    page = ChromiumPage(addr_or_opts=co)
    page.get("https://creator.douyin.com/creator-micro/content/upload")
    time.sleep(10)
    # 登录后才能运行下面的发布代码
    with open("./jsscript/douyinshiping.js", "r", encoding="utf-8") as r:
        zr = r.read()
    # 视频
    video = open(r"./output1.mp4", "rb")
    video_encoded_string = base64.b64encode(video.read()).decode('utf-8')
    # 视频描述
    description = "今天天气真好"
    zr = zr % (video_encoded_string, description)
    page.run_js(zr)


def run_douyintuwen_js():
    """抖音图文发布"""
    chrome_exe_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    co = ChromiumOptions()
    co.set_local_port(60741)
    co.set_browser_path(chrome_exe_path)
    page = ChromiumPage(addr_or_opts=co)
    page.get("https://creator.douyin.com/creator-micro/content/upload?default-tab=3")
    time.sleep(10)
    # 登录后才能运行下面的发布代码
    with open("./jsscript/douyintuwen.js", "r", encoding="utf-8") as r:
        zr = r.read()
    # 图片
    video = open(r"./1.jpg", "rb")
    video_encoded_string = base64.b64encode(video.read()).decode('utf-8')
    # 标题
    title = "今天天气真好"
    zr = zr % (video_encoded_string, title)
    page.run_js(zr)


def run_toutiaoshiping_js():
    """今日头条视频发布"""
    chrome_exe_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    co = ChromiumOptions()
    co.set_local_port(60741)
    co.set_browser_path(chrome_exe_path)
    page = ChromiumPage(addr_or_opts=co)
    page.get("https://mp.toutiao.com/profile_v4/xigua/upload-video")
    time.sleep(10)
    # 登录后才能运行下面的发布代码
    with open("./jsscript/toutiaoshiping.js", "r", encoding="utf-8") as r:
        zr = r.read()
    # 视频
    video = open(r"./output1.mp4", "rb")
    video_encoded_string = base64.b64encode(video.read()).decode('utf-8')
    # # 视频描述
    # description = "今天天气真好"
    zr = zr % (video_encoded_string)
    page.run_js(zr)


def run_toutiaotuwen_js():
    """今日头条图文发布"""
    chrome_exe_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    co = ChromiumOptions()
    co.set_local_port(60741)
    co.set_browser_path(chrome_exe_path)
    page = ChromiumPage(addr_or_opts=co)
    # page.get("https://mp.toutiao.com/profile_v4/xigua/upload-video")
    # time.sleep(10)
    # 登录后才能运行下面的发布代码
    with open("./jsscript/toutiaotuwen.js", "r", encoding="utf-8") as r:
        zr = r.read()
    # 视频
    # video = open(r"C:\Users\vm\Videos\1.mp4", "rb")
    # video_encoded_string = base64.b64encode(video.read()).decode('utf-8')
    # # 视频描述
    # description = "今天天气真好"
    # zr = zr % (video_encoded_string)
    page.run_js(zr)


def run_kuaishoushiping_js():
    """快手视频发布"""
    chrome_exe_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    co = ChromiumOptions()
    co.set_local_port(60741)
    co.set_browser_path(chrome_exe_path)
    page = ChromiumPage(addr_or_opts=co)
    # page.get("https://cp.kuaishou.com/article/publish/video?tabType=1")
    # time.sleep(10)
    # 登录后才能运行下面的发布代码
    with open("./jsscript/kuaishoushiping.js", "r", encoding="utf-8") as r:
        zr = r.read()
    # 视频
    video = open(r"C:\Users\vm\Videos\output1.mp4", "rb")
    video_encoded_string = base64.b64encode(video.read()).decode('utf-8')
    # 视频描述
    description = "今天天气真好"
    zr = zr % (video_encoded_string, description)
    page.run_js(zr)


def run_kuaishoutuwen_js():
    """快手图文发布"""
    chrome_exe_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    co = ChromiumOptions()
    co.set_local_port(60741)
    co.set_browser_path(chrome_exe_path)
    page = ChromiumPage(addr_or_opts=co)
    page.get("https://cp.kuaishou.com/article/publish/video?tabType=2")
    time.sleep(2)
    # 登录后才能运行下面的发布代码
    with open("./jsscript/kuaishoutuwen.js", "r", encoding="utf-8") as r:
        zr = r.read()
    # 图片
    video = open(r"C:\Users\vm\Pictures\1.jpg", "rb")
    video_encoded_string = base64.b64encode(video.read()).decode('utf-8')
    # 标题
    title = "今天天气真好"
    zr = zr % (video_encoded_string, title)
    page.run_js(zr)


if __name__ == '__main__':
    run_bilibilishiping_js()  # 哔哩哔哩视频发布
    # run_bilibilituwen_js()  # 哔哩哔哩图文发布
    # run_tenxunweishi_js()  # 腾讯微视视频发布
    # run_douyinshiping_js()  # 抖音视频发布
    # run_douyintuwen_js()  # 抖音图文发布
    # run_toutiaoshiping_js()  # 今日头条视频发布
    # run_toutiaotuwen_js()  # 今日头条图文发布, 不行
    # run_kuaishoushiping_js()  # 快手视频发布, 不行
    # run_kuaishoutuwen_js()  # 快手图文发布, 不行
