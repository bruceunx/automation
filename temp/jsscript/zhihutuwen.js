/*
* 知乎发布图文*/

/*
* 输入标题内容*/
// 1. 获取 textarea 元素
var textarea = document.querySelector('.Input.i7cW1UcwT6ThdhTakqFm');
// 2. 设置 textarea 的值
textarea.value = '测试标题！！！！';
// 3. 创建一个 input 事件并触发它
var event = new Event('input', { bubbles: true });
textarea.dispatchEvent(event);

/*
* 输入正文内容*/
setTimeout(() => {
    const editableDiv = document.querySelector('.public-DraftStyleDefault-block.public-DraftStyleDefault-ltr');
    if (editableDiv) {
        console.log('Editable Div found:', editableDiv);
        // 更新内容
        editableDiv.innerHTML = '<span data-text="true">生活中的美好往往就藏在这些看似平凡的瞬间</span>';
    } else {
        console.error('Editable Div not found');
    }
}, );

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
const fileInput = document.querySelector('.InputLike.PostEditor.css-j17lau.Editable input[type="file"][accept="image/webp,image/jpg,image/jpeg,image/png,image/gif"]');
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
const event = new Event('change', { bubbles: true });
fileInput.dispatchEvent(event);