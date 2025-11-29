/*
* 快手发布图文*/

/*
* 输入图片*/
const base64String = 'data:image/jpeg;base64,%s';

function base64ToBinary(base64) {
    const base64Data = base64.split(',')[1];
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return byteArray.buffer;
}

/*
* 获取页面上的文件输入元素*/
const draggerContent = document.querySelector('.ant-tabs-tabpane.ant-tabs-tabpane-active');

if (draggerContent) {
    console.log('Dragger content element found:', draggerContent);

    // 找到上传按钮<button class="_upload-btn_dd2iu_68">上传图片</button>
    const uploadButton = draggerContent.querySelector('._upload-btn_dd2iu_68');

    if (uploadButton) {
        console.log('Upload button element found:', uploadButton);

        // 模拟点击上传按钮
        uploadButton.click();

        const fileInput = document.querySelector('.ant-tabs-tabpane-active input[type="file"][accept="image/png, image/jpg, image/jpeg, image/webp"]');
        console.log('fileInput found:', fileInput);
        /*
        * 将Base64字符串转换为二进制数据*/
        const binaryData = base64ToBinary(base64String);
        /*
        * 创建Blob对象表示图片数据*/
        const blob = new Blob([binaryData], { type: 'image/jpeg' });
        /*
        * 创建File对象表示上传的图片文件*/
        const file = new File([blob], 'C:/Users/Administrator/Desktop/1.png', { type: 'image/jpeg' });
        /*
        * 创建FileList对象来模拟文件列表*/
        const fileList = [file];
        /*
        * 设置文件输入元素的files属性*/
        Object.defineProperty(fileInput, 'files', {
            value: fileList,
            writable: true
        });
        /*
        * 触发文件选择事件*/
        const event = new Event('change', { bubbles: true });
        fileInput.dispatchEvent(event);

        // 在触发文件选择事件后延迟关闭文件选择框
        setTimeout(() => {
            // 获取当前活动的元素
            const activeElement = document.activeElement;

            // 如果当前活动的元素是文件输入框，则模拟点击事件关闭文件选择框
            if (activeElement === fileInput) {
                activeElement.blur();
                document.body.click();
                console.log('File selection dialog closed');
            }
        }, 100); // 延迟100毫秒

        console.log('File uploaded successfully');
    } else {
        console.error('Upload button element not found');
    }
} else {
    console.error('Dragger content element not found');
}

/*
* 输入正文内容*/
setTimeout(() => {
    // 找到可编辑区域
    const editableContainer = document.querySelector('.ant-tabs-tabpane-active ._edit-form-item_1ne7e_7 ._edit-desc-container_1ne7e_45 ._description_1ne7e_62[contenteditable="true"]');
    if (editableContainer) {
    console.log('Editable container element found:', editableContainer);

    // 定义要输入的内容
    const content = '%s';

    // 使用 setTimeout 延迟执行输入操作
    setTimeout(() => {
        // 清空现有内容
        editableContainer.innerHTML = '';

        // 插入新内容
        editableContainer.innerHTML = content;

        // 触发 input 事件以确保内容更新
        const inputEvent = new Event('input', { bubbles: true });
        editableContainer.dispatchEvent(inputEvent);

        console.log('Content inserted successfully');
    });}
    else {
        console.error('Editable container element not found');
    }
}, 2000);

/*
* 发布*/
setTimeout(() => {
    document.querySelector('._footer_brvce_20 .ant-btn.ant-btn-primary').click();
}, 3000);