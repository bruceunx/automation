/*
* 头条号发布图文*/

/*
* 点击图片上传*/
const button = document.querySelector('.syl-toolbar-tool.image.static .syl-toolbar-button');
button.click();
/*
* 上传图片*/
setTimeout(()=> {
    const base64String = 'data:image/jpeg;base64,%s';
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
    const fileInput = document.querySelector('.btn-upload-handle.upload-handler input[type="file"][accept="image/*"]');
    const binaryData = base64ToBinary(base64String);
    const blob = new Blob([binaryData], {type: 'image/jpeg'});
    const file = new File([blob], 'C:/Users/vm/Pictures/1.jpg', {type:'image/jpg'});
    const fileList = new DataTransfer();
    fileList.items.add(file);
    fileInput.files = fileList.files;
    const event = new Event('change', { bubbles: true });
    fileInput.dispatchEvent(event);
    setTimeout(() => {
    // 选择按钮元素
    const button = document.querySelector('[data-e2e="imageUploadConfirm-btn"]');
    if (button) {
        console.log('Button found:', button);
        // 触发点击事件
        button.click();
    } else {
        console.error('Button not found');
    }
    }, 3000);
    /*
    * 输入标题内容*/
    const targetDiv = document.querySelector('.editor-title.autofit-textarea-wrapper');
    if (targetDiv) {
        console.log('Target div found:', targetDiv);
        // 获取内部的 <pre> 和 <textarea> 元素
        const preElement = targetDiv.querySelector('pre');
        const textAreaElement = targetDiv.querySelector('textarea');

        if (preElement && textAreaElement) {
            // 定义要输入的内容
            const content = '这是新标题';
            // 更新 <pre> 元素的内容
            preElement.innerHTML = content;
            // 触发 input 事件以确保内容更新
            const inputEvent = new Event('input', { bubbles: true });
            preElement.dispatchEvent(inputEvent);
            console.log('Pre content updated successfully');
            // 更新 <textarea> 元素的内容
            textAreaElement.innerHTML = content;
            // 触发 input 事件以确保内容更新
            const inputEvent2 = new Event('input', { bubbles: true });
            textAreaElement.dispatchEvent(inputEvent2);
            console.log('Textarea content updated successfully');
        } else {
            console.error('Pre or textarea element not found');
        }
    } else {
        console.error('Target div not found');
    }

    /*
    * 输入正文内容*/
    const editableDiv = document.querySelector('.ProseMirror[contenteditable="true"]');
    console.log('Editable Div found:', editableDiv);
    const newContent = '<p>生活中的美好往往就藏在这些看似平凡的瞬间1111</p>';
    editableDiv.innerHTML = newContent;
    /*
    * 选择单标题和无封面*/
    let list = document.querySelectorAll('.byte-radio > span')
    list[0].click()
    list[4].click()
    /*
    * 发布*/
    if (newContent.length > 300) {
        setTimeout(() => {
            document.querySelector('.byte-btn.byte-btn-primary.byte-btn-size-large.byte-btn-shape-square.publish-btn.publish-btn-last').click();
        }, 4000);
        setTimeout(() => {
            document.querySelector('.byte-btn.byte-btn-primary.byte-btn-size-large.byte-btn-shape-square.publish-btn.publish-btn-last').click();
        }, 6000);
    }
    else {
        setTimeout(() => {
        document.querySelector('.byte-btn.byte-btn-primary.byte-btn-size-large.byte-btn-shape-square.publish-btn.publish-btn-last').click();
        }, 4000);
        setTimeout(() => {
        let d = document.querySelector('.byte-modal-footer .byte-btn')
        d.click()
        }, 7000);
        setTimeout(() => {
            document.querySelector('.byte-btn.byte-btn-primary.byte-btn-size-large.byte-btn-shape-square.publish-btn.publish-btn-last').click();
        }, 9000);
    }
}, 1000);


