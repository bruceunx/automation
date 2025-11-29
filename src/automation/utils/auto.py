JsBilibiliVideo = """
const base64String = 'data:video/mp4;base64,%s';
function base64ToBinary(base64) {
    const base64Data = base64.split(',')[1];
    const byteCharacters = atob(base64Data);
    const byteArrays = [];
    for (let offset = 0; offset < byteCharacters.length; offset += 512) {
        const slice = byteCharacters.slice(offset, offset + 512);
        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        };
        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    };
    const result = new Uint8Array(byteArrays.reduce((acc, curr) => acc + curr.length, 0));
    let offset = 0;
    byteArrays.forEach(bytes => {
        result.set(bytes, offset);
        offset += bytes.length;
    });
    return result.buffer;
};

const fileInput = document.querySelector('.bcc-upload-wrapper input[type="file"][accept=".mp4,.flv,.avi,.wmv,.mov,.webm,.mpeg4,.ts,.mpg,.rm,.rmvb,.mkv,.m4v"]');
const binaryData = base64ToBinary(base64String);
const blob = new Blob([binaryData], {type: 'video/mp4'});
const file = new File([blob], '%s.mp4', {type:'video/mp4'});
const fileList = new DataTransfer();
fileList.items.add(file);
fileInput.files = fileList.files;
const event = new Event('change', { bubbles: true });
fileInput.dispatchEvent(event);

setTimeout(() => {
    // 获取顶层容器元素
    const tagInputWrp = document.querySelector('.tag-input-wrp');
    if (tagInputWrp) {
        console.log('Tag Input Wrapper found:', tagInputWrp);

        // 获取 .input-instance 中的 input 元素
        const inputInstance = tagInputWrp.querySelector('.input-instance input[type="text"]');
        if (inputInstance) {
            console.log('Input Instance found:', inputInstance);
            // 在输入框中添加标签
            inputInstance.value = '日常';
            // 模拟回车键事件
            const enterKeyEvent = new KeyboardEvent('keydown', {
                bubbles: true,
                cancelable: true,
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13
            });
            inputInstance.dispatchEvent(enterKeyEvent);

            console.log('标签已添加');
        } else {
            console.error('Input Instance not found');
        }
    } else {
        console.error('Tag Input Wrapper not found');
    }
}, 5000);

setTimeout(() => {
    // 获取顶层容器元素
    const submitContainer = document.querySelector('.submit-container');
    if (submitContainer) {
        console.log('Submit Container found:', submitContainer);
        // 获取“立即投稿”按钮
        const submitButton = submitContainer.querySelector('.submit-add');
        if (submitButton) {
            console.log('Submit Button found:', submitButton);
            // 触发点击事件
            submitButton.click();
            console.log('“立即投稿”按钮已点击');
        } else {
            console.error('“立即投稿”按钮未找到');
        }
    } else {
        console.error('Submit Container not found');
    }
}, 6000);

"""
