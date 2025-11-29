import json
import asyncio
import base64

from PySide6.QtCore import QObject, Signal

from playwright.async_api import BrowserContext, Page, async_playwright
from qasync import asyncSlot

from utils.auto import JsBilibiliVideo
from utils.constant import Platform, PublishType

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


async def automation_bilibili_video(page: Page, user: dict):
    await page.goto(user["publish_url"])
    await page.wait_for_load_state("networkidle")
    with open(user["video_path"], "rb") as video_file:
        encoded_video = base64.b64encode(video_file.read()).decode("utf-8")

    formatted_js = JsBilibiliVideo % (encoded_video, user["title"])
    await page.evaluate(formatted_js)
    await page.wait_for_timeout(7000)
    await page.wait_for_load_state("networkidle")


async def automation_zh_video(page: Page, user: dict):
    await page.goto(user["publish_url"])

    await page.set_input_files("input.VideoUploadButton-fileInput", user["video_path"])

    await page.wait_for_selector('div:has-text("上传成功")')

    #######################################################################
    #
    await page.click("div.VideoUploadForm-imageEditButton")

    await page.wait_for_selector("div.VideoCoverEditor-Modal")
    await page.click("div.css-fmjg5z")

    await page.set_input_files("input[type='file'].css-1s4ntcx", user["image_cover"])
    await page.wait_for_selector("button:has-text('确认选择')")
    await page.click("button:has-text('确认选择')")
    await page.wait_for_load_state("networkidle")
    await page.fill('input[placeholder="输入视频标题"]', user["title"])

    await page.click(".VideoUploadForm-input.VideoUploadForm-input--multiline")
    await page.type(
        ".VideoUploadForm-input.VideoUploadForm-input--multiline", user["content"]
    )

    #
    await page.click("button#Popover8-toggle.Button")
    await page.wait_for_selector("div#Popover8-content")

    # button_text = '科技数码'
    #
    # page.click(f'div.Select-list.VideoUploadForm-selectList button:has-text("{button_text}")')
    await page.click("div#Popover8-content button:nth-of-type(2)")

    await page.wait_for_selector("button#Popover10-toggle.Button")
    await page.click("button#Popover10-toggle.Button")

    await page.wait_for_selector("div#Popover10-content")

    await page.click("div#Popover10-content button:nth-of-type(2)")

    await page.click("button.TopicInputAlias-placeholderButton")

    await page.type("div.TopicInputAlias-autocomplete", "1FD")

    await page.wait_for_selector("div.AutoComplete-menu")
    await page.click("div.AutoComplete-menu div:first-child")

    await page.click("label.VideoUploadForm-radioLabel")

    await page.wait_for_load_state("networkidle")
    await page.click('button:has-text("发布视频")')
    await page.wait_for_load_state("networkidle")


async def automation_xg_video(page: Page, user: dict):
    await page.goto(user["publish_url"])

    await page.click("svg.close")
    await page.set_input_files('input[type="file"]', user["video_path"])
    await page.wait_for_function(
        "document.querySelector('.status') && document.querySelector('.status').innerText === '上传成功'"
    )
    await page.click("div.mentionText")
    await page.type("div.mentionText", user["title"])
    await page.click("div.m-xigua-upload")
    await page.click("li:has-text('本地上传')")
    await page.set_input_files(
        "div.byte-upload input[type='file']", user["image_cover"]
    )
    try:
        await page.wait_for_selector("div.clip-btn-content", timeout=2000)
        await page.click("div.clip-btn-content")
    except Exception:
        pass
    await page.wait_for_selector("button.btn-sure")
    await page.click("button.btn-sure")
    await page.click("div.footer button:has-text('确定')")
    await page.wait_for_selector("div.m-xigua-upload div.bg")

    checkbox = page.locator(
        "label.byte-checkbox:has-text('同步到抖音') input[type='checkbox']"
    )
    if checkbox.is_checked():
        await page.click("label.byte-checkbox")
    await page.click("button.action-footer-btn")
    await page.wait_for_load_state("networkidle")


async def automation_bili_image(page: Page, user: dict):
    await page.goto(user["publish_url"])
    await page.click("input.bili-dyn-publishing__title__input")
    await page.type(
        "input.bili-dyn-publishing__title__input",
        user["title"],
    )
    await page.click("div.bili-rich-textarea__inner")
    await page.type(
        "div.bili-rich-textarea__inner",
        user["content"],
    )

    async def handle_file_chooser(file_chooser):
        await file_chooser.set_files(user["image_cover"])

    page.on("filechooser", handle_file_chooser)

    await page.click("div.bili-dyn-publishing__tools__item.pic")
    await page.wait_for_timeout(1000)

    await page.click("div.bili-dyn-publishing__action.launcher")
    await page.wait_for_selector(
        "button.bili-dyn-specification-popup__btn.bili-button.primary.bili-button--medium"
    )
    await page.click(
        "button.bili-dyn-specification-popup__btn.bili-button.primary.bili-button--medium"
    )

    await page.wait_for_timeout(3000)


async def automation_zh_image(page: Page, user: dict):
    # handle import docx file
    await page.goto(user["publish_url"])

    await page.click(".Input.i7cW1UcwT6ThdhTakqFm")
    await page.type(".Input.i7cW1UcwT6ThdhTakqFm", user["title"])
    await page.click("div.DraftEditor-root")
    await page.type("div.DraftEditor-root", user["content"])

    await page.set_input_files("input[type='file']", user["image_cover"])
    await page.set_input_files("input.UploadPicture-input", user["image_cover"])

    await page.click("button.css-1gtqxw0")
    await page.wait_for_selector('input[aria-label="搜索话题"]')
    await page.type('input[aria-label="搜索话题"]', "1FD")
    await page.wait_for_selector("div.css-ogem9c")
    await page.click("div.css-ogem9c button:first-child")

    await page.click('button:has-text("发布")')

    await page.wait_for_timeout(3000)


async def automation_wx_image(page: Page, user: dict):
    await page.goto(user["publish_url"])

    await page.click("div.new-creation__menu > div:nth-of-type(2)")

    new_page = await page.context.wait_for_event("page")
    await new_page.wait_for_load_state("load")

    await new_page.click("div#js_title_main")
    await new_page.type("div#js_title_main", user["title"])

    author = "admin"
    if "setting" in user:
        author = user["setting"].get("author", "admin")
        if len(author) == 0:
            author = "admin"
    await new_page.click("div#js_author_area")
    await new_page.type("div#js_author_area", author)

    await new_page.click("div#edui1_iframeholder")
    await new_page.type("div#edui1_iframeholder", user["content"])

    await new_page.hover("#js_cover_area")
    await new_page.wait_for_selector(".pop-opr__group.js_cover_null_pop")

    second_li_selector = ".pop-opr__group.js_cover_null_pop ul > li:nth-child(2)"

    await new_page.click(second_li_selector)
    await new_page.wait_for_selector(
        "a.weui-desktop-menu__link.weui-desktop-menu__link_current", timeout=10000
    )
    await new_page.click("a.weui-desktop-menu__link.weui-desktop-menu__link_current")

    def handle_file_chooser(file_chooser):
        file_chooser.set_files(user["image_cover"])

    await new_page.on("filechooser", handle_file_chooser)
    new_page.click(
        "div.js_upload_btn_container.weui-desktop-upload-input__wrp.webuploader-container"
    )

    await new_page.wait_for_timeout(5000)
    await new_page.click(
        "button.weui-desktop-btn.weui-desktop-btn_primary:has-text('下一步')"
    )
    await new_page.wait_for_timeout(2000)
    await new_page.click(
        "button.weui-desktop-btn.weui-desktop-btn_primary:has-text('完成')"
    )
    await new_page.wait_for_timeout(3000)
    await new_page.wait_for_selector("button.mass_send", timeout=10000)
    await new_page.click("button.mass_send")

    #############################################################
    # first post
    # new_page.wait_for_selector(
    #     'a.btn.btn_primary.js_btn:has-text("同意以上声明")', timeout=10000)
    #
    # new_page.click('a.btn.btn_primary.js_btn')

    await new_page.wait_for_selector("div.mass-send__td")

    if await new_page.query_selector(
        "label.weui-desktop-form__label:has-text('分组通知')"
    ):
        await new_page.click("div.mass-send__timer-wrp")

    await new_page.wait_for_timeout(1000)
    await new_page.click(
        "button.weui-desktop-btn.weui-desktop-btn_primary:has-text('发表')"
    )

    await new_page.wait_for_timeout(1000)  # Adjust wait time as necessary
    await new_page.click(
        "button.weui-desktop-btn.weui-desktop-btn_primary:has-text('继续发表')"
    )
    await new_page.wait_for_selector(".js_qrcode", timeout=5000)

    image_element = await new_page.query_selector(".js_qrcode")
    if image_element:
        await image_element.screenshot(path="wx_screenshot.png")
    await new_page.wait_for_timeout(3000)


async def automation_xhs_video(page: Page, user: dict):
    await page.goto(user["publish_url"])

    # check set video_path in user
    await page.set_input_files("input.upload-input", user["video_path"])

    await page.locator('input.d-text[placeholder="填写标题会有更多赞哦～"]').fill(
        user["title"]
    )

    await page.locator("div.topic-container").click()

    await page.type(
        "div.topic-container",
        user["content"],
    )

    is_public = 1
    if "setting" in user:
        is_public = user["setting"].get("is_public", 1)
    if is_public == 0:
        await page.locator("div.flexbox.mt12 div label").nth(1).click()
    await page.wait_for_load_state("networkidle")
    await page.locator("button.publishBtn").click()
    await page.wait_for_load_state("networkidle")


async def automation_xhs_image(page: Page, user: dict):
    await page.goto(user["publish_url"])

    second_creator_tab = page.locator("div.creator-tab")
    await second_creator_tab.nth(1).click()
    if "images" in user:
        await page.set_input_files("input.upload-input", user["images"])
    else:
        await page.set_input_files("input.upload-input", user["image_cover"])

    await page.locator("input.el-input__inner").nth(0).fill(user["title"])

    await page.locator("div.topic-container").click()

    await page.type(
        "div.topic-container",
        user["content"],
    )

    is_public = 1
    if "setting" in user:
        is_public = user["setting"].get("is_public", 1)
    if is_public == 0:
        await page.locator("div.flexbox.mt12 div label").nth(1).click()
    btn = page.locator("button.publishBtn")
    await page.wait_for_load_state("networkidle")
    await btn.click()
    await page.wait_for_load_state("networkidle")


def get_process_fun(platform: Platform, platform_type: PublishType):
    match platform_type:
        case PublishType.Article:
            match platform:
                case Platform.XHS:
                    return automation_xhs_image
                case Platform.WX:
                    return automation_wx_image
                case Platform.ZH:
                    return automation_zh_image
                case Platform.BiliBili:
                    return automation_bili_image
                case _:
                    raise ValueError("not support platform")
        case PublishType.HorizonVideo:
            match platform:
                case Platform.XHS:
                    return automation_xhs_video
                case Platform.XG:
                    return automation_xg_video
                case Platform.ZH:
                    return automation_zh_video
                case Platform.BiliBili:
                    return automation_bilibili_video
                case _:
                    raise ValueError("not support platform")
        case _:
            raise ValueError("not support type")


class PublishWorker(QObject):
    progress_updated = Signal(int)
    task_completed = Signal(list)
    error_occurred = Signal(str)
    finished = Signal()

    def __int__(self, parent=None):
        super(PublishWorker, self).__int__(parent)
        self.completed_tasks = 0
        self.total_tasks = 0

    async def process_single_page(
        self,
        context: BrowserContext,
        user: dict,
    ):
        result = {
            "user_id": user["id"],
            "title": user["title"],
            "content": user["content"],
            "status": 0,
        }
        try:
            page = await context.new_page()
            await context.add_cookies(json.loads(user["cookies"]))
            func = get_process_fun(user["platform"], user["publish_type"])
            await func(page, user)
            result["status"] = 1
        except Exception as e:
            print("error from single page", e)

        finally:
            self.completed_tasks += 1
            progress = int((self.completed_tasks / self.total_tasks) * 100)
            self.progress_updated.emit(progress)
            await page.close()

        return result

    @asyncSlot(list)
    async def handle_publish(self, users):
        await self.process_urls_parallel(users)

    async def process_urls_parallel(self, users: list, max_concurrent: int = 3):
        self.completed_tasks = 0
        self.total_tasks = len(users)

        async with async_playwright() as p:
            browser = await p.chromium.launch(executable_path=EDGE_PATH, headless=False)
            context = await browser.new_context()

            try:
                # Create a semaphore to limit concurrent tasks
                semaphore = asyncio.Semaphore(max_concurrent)

                async def process_with_semaphore(user):
                    async with semaphore:
                        return await self.process_single_page(context, user)

                tasks = [process_with_semaphore(user) for user in users]

                results = await asyncio.gather(*tasks)
                self.task_completed.emit(results)

            except Exception as e:
                self.error_occurred.emit(str(e))
                print("error", e)
            finally:
                await context.close()
                await browser.close()
                self.finished.emit()
