from enum import Enum


class EmpployeeType(Enum):
    FullTime = 1
    PartTime = 2
    OnTry = 3

    @property
    def verbose(self) -> str:
        return ("全职", "兼职", "试用期")[self.value - 1]

    @classmethod
    def from_value(cls, value: int) -> "EmpployeeType":
        return cls(value)

    @classmethod
    def from_str(cls, text: str) -> "EmpployeeType":
        match text:
            case "全职":
                return EmpployeeType.FullTime
            case "兼职":
                return EmpployeeType.PartTime
            case _:
                return EmpployeeType.OnTry


class Platform(Enum):
    BiliBili = 0
    WX = 1
    DY = 2
    KS = 3
    TXWS = 4
    TT = 5
    XG = 6
    XHS = 7
    ZH = 8

    @property
    def display_name(self) -> str:
        return (
            "哔哩哔哩",
            "微信公众号",
            "抖音",
            "快手视频",
            "腾讯微视",
            "头条",
            "西瓜视频",
            "小红书",
            "知乎",
        )[self.value]

    @classmethod
    def from_str(cls, title: str) -> "Platform":
        match title.lower():
            case "xhs":
                return cls.XHS
            case "bilibili":
                return cls.BiliBili
            case "wx":
                return cls.WX
            case "xg":
                return cls.XG
            case "zh":
                return cls.ZH
            case "dy":
                return cls.DY
            case "ks":
                return cls.KS
            case "txws":
                return cls.TXWS
            case "tt":
                return cls.TT
            case _:
                raise ValueError("platform not support")

    @classmethod
    def from_value(cls, value: int) -> tuple["Platform", str]:
        try:
            platform = cls(value)
            return platform, platform.display_name
        except ValueError:
            raise ValueError("unknown platform")

    @classmethod
    def from_value_to_platform(cls, value: int) -> "Platform":
        try:
            return cls(value)
        except ValueError:
            raise ValueError("unknown platform")


class PublishType(Enum):
    Article = 0
    HorizonVideo = 1
    VerticalVideo = 2
    ShortNote = 3

    @property
    def verbose(self) -> str:
        return ("图文", "横版短视频", "竖版小视频", "短内容")[self.value]

    @classmethod
    def from_value(cls, value: int) -> "PublishType":
        try:
            return cls(value)
        except ValueError:
            raise ValueError("unknown publish type")


LOGIN_METADATA = {
    Platform.BiliBili: {
        "url": "https://passport.bilibili.com/login?gourl=https%3A%2F%2Faccount.bilibili.com%2Faccount%2Fhome",
        "creator_url": "https://member.bilibili.com/platform/home",
        "cookie_url": "https://member.bilibili.com",
        "prefix": "bilibili",
        "script": """
        (function() {
            var name_element = document.getElementsByClassName('home-top-msg-name')[0];
            var img_element = document.querySelector('div.home-head');
            var img = img_element ? img_element.querySelector('img') : null;
            return JSON.stringify({ name: name_element ? name_element.textContent : '', avatar: img ? img.src : '' });
        })();
        """,
        "title": "哔哩哔哩",
        "icon": "assets/icons/bilibili.svg",
        "publish_url_image": "https://t.bilibili.com",
        "publish_url_video": "https://member.bilibili.com/platform/upload/video/frame?page_from=creative_home_top_upload",
        "selector": "div.tips-calendar_wrap",
    },
    Platform.WX: {
        "url": "https://mp.weixin.qq.com",
        "creator_url": "https://mp.weixin.qq.com",
        "cookie_url": "https://mp.weixin.qq.com/",
        "prefix": "wx",
        "script": """
        (function() {
            var divElement = document.querySelector('div.weui-desktop-person_info')
            var name_element = divElement ? divElement.querySelector('div.weui-desktop_name') : null;
            var img = divElement ? divElement.querySelector('img.weui-desktop-account__img') : null;
            return JSON.stringify({ name: name_element ? name_element.textContent : '', avatar: img ? img.src : '' });
        })();
        """,
        "title": "微信公众号",
        "icon": "assets/icons/wx.svg",
        "publish_url_image": "https://mp.weixin.qq.com/",
        "selector": "div.weui-desktop_name",
    },
    Platform.DY: {
        "url": "https://creator.douyin.com",
        "creator_url": "https://creator.douyin.com",
        "cookie_url": "https://creator.douyin.com",
        "prefix": "dy",
        "script": """
        (function() {
            var name_element = document.querySelector('div.rNsML');
            var img = document.querySelector('img.f3hat');
            return JSON.stringify({ name: name_element ? name_element.textContent : '', avatar: img ? img.src : '' });
        })();
        """,
        "title": "抖音",
        "icon": "assets/icons/dy.svg",
        "selector": "div.rNsML",
    },
    Platform.KS: {
        "url": "https://passport.kuaishou.com/pc/account/login/?sid=kuaishou.web.cp.api&callback=https%3A%2F%2Fcp.kuaishou.com%2Frest%2Finfra%2Fsts%3FfollowUrl%3Dhttps%253A%252F%252Fcp.kuaishou.com%252Fprofile%26setRootDomain%3Dtrue",
        "creator_url": "https://cp.kuaishou.com/profile",
        "cookie_url": "https://cp.kuaishou.com",
        "prefix": "ks",
        "script": """
        (function() {
            var div_element = document.querySelector('div.header-info-card');
            var name_element = div_element ? div_element.querySelector('div.user-name') : null;
            var img = div_element ? div_element.querySelector('img') : null;
            return JSON.stringify({ name: name_element ? name_element.textContent : '', avatar: img ? img.src : '' });
        })();
        """,
        "title": "快手视频",
        "icon": "assets/icons/ks.svg",
        "selector": "div.info-top-name",
    },
    Platform.TXWS: {
        "url": "https://h5.weishi.qq.com/weishi/account/login?r_url=http%3A%2F%2Fmedia.weishi.qq.com%2F",
        "creator_url": "https://media.weishi.qq.com",
        "cookie_url": "https://media.weishi.qq.com",
        "prefix": "txws",
        "script": """
        (function() {
            var div_element = document.querySelector('div.container___R5xBA');
            var name_element = div_element ? div_element.querySelector('div.user-name___2QHja') : null;
            var img = div_element ? div_element.querySelector('img') : null;
            return JSON.stringify({ name: name_element ? name_element.textContent : '', avatar: img ? img.src : '' });
        })();
        """,
        "title": "腾讯微视",
        "icon": "assets/icons/txws.svg",
        "selector": "div.icon.upload",
    },
    Platform.TT: {
        "url": "https://mp.toutiao.com/auth/page/login",
        "creator_url": "https://mp.toutiao.com/profile_v4/index",
        "cookie_url": "https://mp.toutiao.com",
        "prefix": "tt",
        "script": """
        (function() {
            var name_element = document.querySelector('div.auth-avator-name');
            var img = document.querySelector('img.auth-avator-img');
            return JSON.stringify({ name: name_element ? name_element.textContent : '', avatar: img ? img.src : '' });
        })();
        """,
        "title": "头条",
        "icon": "assets/icons/tt.svg",
        "selector": "img.auth-avator-img",
    },
    Platform.XG: {
        "url": "https://studio.ixigua.com",
        "creator_url": "https://studio.ixigua.com/",
        "cookie_url": "https://studio.ixigua.com/",
        "prefix": "xg",
        "script": """
        (function() {
            var name_element = document.querySelector('div.user-info__username');
            var div_element = document.querySelector('div.img-wrapper');
            var img = div_element ? div_element.querySelector('img') : null;
            return JSON.stringify({ name: name_element ? name_element.textContent : '', avatar: img ? img.src : '' });
        })();
        """,
        "title": "西瓜视频",
        "icon": "assets/icons/xg.svg",
        "publish_url_video": "https://studio.ixigua.com/upload?from=post_article",
        "selector": "div.user-info__username",
    },
    Platform.XHS: {
        "url": "https://creator.xiaohongshu.com",
        "creator_url": "https://creator.xiaohongshu.com/new/home",
        "cookie_url": "https://www.xiaohongshu.com",
        "prefix": "xhs",
        "script": """
        (function() {
            var name_element = document.getElementsByClassName('account-name')[0];
            var img_element = document.getElementsByClassName('avatar')[0];
            var img = img_element ? img_element.getElementsByTagName('img')[0] : null;
            return JSON.stringify({ name: name_element ? name_element.textContent : '', avatar: img ? img.src : '' });
        })();
        """,
        "title": "小红书",
        "icon": "assets/icons/xhs.svg",
        "publish_url_image": "https://creator.xiaohongshu.com/publish/publish",
        "publish_url_video": "https://creator.xiaohongshu.com/publish/publish",
        "selector": "div.account-name",
    },
    Platform.ZH: {
        "url": "https://www.zhihu.com/creator",
        "creator_url": "https://www.zhihu.com/creator",
        "cookie_url": "https://www.zhihu.com/creator",
        "prefix": "zh",
        "script": """
        (function() {
            var name_element = document.querySelector('div.LevelInfoV2-creatorInfo.css-sbvk4m');
            var img = document.querySelector('img.Avatar');
            return JSON.stringify({ name: name_element ? name_element.textContent : '', avatar: img ? img.src : '' });
        })();
        """,
        "title": "知乎",
        "icon": "assets/icons/zh.svg",
        "publish_url_image": "https://zhuanlan.zhihu.com/write",
        "publish_url_video": "https://www.zhihu.com/zvideo/upload-video",
        "selector": "div.LevelInfoV2-creatorInfo.css-sbvk4m",
    },
}
