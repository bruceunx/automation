/*
* 抖音发布视频*/

/*
* 上传视频*/
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
const fileInput = document.querySelector('.container-drag-AOMYqU input[type="file"][accept="video/*"]');
const binaryData = base64ToBinary(base64String);
const blob = new Blob([binaryData], {type: 'video/mp4'});
const file = new File([blob], 'C:/Users/Administrator/Desktop/output1.mp4', {type:'video/mp4'});
const fileList = new DataTransfer();
fileList.items.add(file);
fileInput.files = fileList.files;
const event = new Event('change', { bubbles: true });
fileInput.dispatchEvent(event);


/*
* 输入正文内容*/
setTimeout(() => {
    // 获取顶层容器元素
    const container = document.querySelector('.zone-container.editor-kit-container[data-placeholder="添加作品简介"]');
    if (container) {
        console.log('Container found:', container);
        // 移除 data-placeholder 属性
        container.removeAttribute('data-placeholder');
        // 选择 `.ace-line` 下的第一个 `span` 元素
        const targetSpan = container.querySelector('.ace-line span[data-string="true"]');
        if (targetSpan) {
            console.log('Target Span found:', targetSpan);
            // 更新内容
            targetSpan.textContent = '%s';
        } else {
            console.error('Target Span not found');
        }
    } else {
        console.error('Container not found');
    }
}, 3000);

/** 发布*/
setTimeout(() => {
    document.querySelector('.button-dhlUZE.primary-cECiOJ.fixed-J9O8Yw').click();
}, 5000);
