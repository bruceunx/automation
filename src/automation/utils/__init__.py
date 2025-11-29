from .constant import Platform, LOGIN_METADATA

PERMISSION = (
    ("权限设置",),
    ("数据面板",),
    ("账号中心",),
    ("账号管理", "账号操作"),
    ("人员管理", "编辑部门"),
    ("数据统计", "数据概览", "发文统计", "账号数据"),
    ("内容管理",),
    ("全选",),
)


def transform_permissions_to_str(permission: int) -> list[str]:
    permission_strs = []
    for part in PERMISSION[:-1]:
        if len(part) == 1:
            permission_strs.append(part[0])
        else:
            permission_strs.extend(part[1:])

    binary_str = bin(permission)[2:].zfill(len(permission_strs))

    selected_items = []
    for bit, item in zip(binary_str, permission_strs):
        if bit == "1":
            selected_items.append(item)

    return selected_items
