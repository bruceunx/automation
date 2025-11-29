/*
* 腾讯微视*/
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

const fileInput = document.querySelector('.container___2ZPI4 input[type="file"][accept="video/mp4,video/x-m4v,video/webm,video/quicktime"]');
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
    // 找到可编辑区域
    const editableContainer = document.querySelector('.ant-mentions textarea');
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
//    document.querySelector('.ant-btn.ant-btn-primary').click();
    document.querySelector('button[class="ant-btn ant-btn-primary"]').click();
}, 3000);
