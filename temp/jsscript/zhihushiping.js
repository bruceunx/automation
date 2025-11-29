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

const fileInput = document.querySelector('.VideoUploadHint-buttonGroup input[type="file"][accept=".3gp,.asf,.avi,.dat,.f4v,.flv,.m4v,.mkv,.mov,.mp4,.mp4v,.mpe,.mpeg,.mpg,.ra,.ram,.rm,.rmvb,.vob,.webm,.wm,.wmv"]');
const binaryData = base64ToBinary(base64String);
const blob = new Blob([binaryData], {type: 'video/mp4'});
const file = new File([blob], '测试视频111.mp4', {type:'video/mp4'});
const fileList = new DataTransfer();
fileList.items.add(file);
fileInput.files = fileList.files;
const event = new Event('change', { bubbles: true });
fileInput.dispatchEvent(event);

/*
* 选择所属领域*/
setTimeout(() => {
    // 获取领域选择按钮
    const selectButton = document.querySelector('.Select-button');
    if (selectButton) {
        console.log('Select Button found:', selectButton);
        // 触发点击事件以显示下拉菜单
        selectButton.click();
        // 等待下拉菜单出现
        setTimeout(() => {
            // 找到并选择特定的领域选项
            const optionToSelect = document.querySelector('.Popover .Select-option[value="生活"]');
            if (optionToSelect) {
                console.log('Option to select found:', optionToSelect);
                // 触发点击事件以选择领域
                optionToSelect.click();
                console.log('领域已选择为“生活”');
            } else {
                console.error('特定领域选项未找到');
            }
        }, 500); // 等待下拉菜单出现的时间
    } else {
        console.error('Select Button not found');
    }
}, 3000);
/*
* 绑定话题*/
setTimeout(() => {
    // 获取原始状态中的按钮
    const originalButton = document.querySelector('.TopicInputAlias-placeholderButton');
    if (originalButton) {
        console.log('Original Button found:', originalButton);

        // 创建一个新的div来模拟绑定的话题
        const topicDiv = document.createElement('div');
        topicDiv.className = 'Tag css-1uzsysq';
        const spanContent = document.createElement('span');
        spanContent.className = 'Tag-content';
        const link = document.createElement('a');
        link.href = "//www.zhihu.com/topic/19554902";
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "日常生活";
        spanContent.appendChild(link);

        // 创建关闭按钮
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'css-19gsiz1';
        const closeSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        closeSvg.setAttribute("width", "1.2em");
        closeSvg.setAttribute("height", "1.2em");
        closeSvg.setAttribute("viewBox", "0 0 24 24");
        closeSvg.className = 'Zi Zi--Close';
        closeSvg.style.fill = 'currentColor';
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", "M5.619 4.381A.875.875 0 1 0 4.38 5.62L10.763 12 4.38 18.381A.875.875 0 1 0 5.62 19.62L12 13.237l6.381 6.382a.875.875 0 1 0 1.238-1.238L13.237 12l6.382-6.381A.875.875 0 0 0 18.38 4.38L12 10.763 5.619 4.38Z");
        closeSvg.appendChild(path);
        closeButton.appendChild(closeSvg);

        topicDiv.appendChild(spanContent);
        topicDiv.appendChild(closeButton);

        // 在原始按钮前插入新div
        originalButton.parentNode.insertBefore(topicDiv, originalButton);

        // 修改按钮文本
        originalButton.querySelector('span').textContent = '绑定话题（1/6）';

        console.log('状态已转换为改变后的状态');
    } else {
        console.error('Original Button not found');
    }
}, 5000);

/*
* 选择视频类型*/
setTimeout(() => {
    // 获取原始状态中的第一个单选按钮
    const radioLabels = document.querySelectorAll('.VideoUploadForm-radioLabel');
    if (radioLabels.length > 0) {
        const firstRadioLabel = radioLabels[0];
        const radioButton = firstRadioLabel.querySelector('.RadioButton');

        if (radioButton) {
            console.log('First Radio Button found:', radioButton);

            // 修改SVG图标
            const svgIcon = radioButton.querySelector('.ZDI--RadioButtonOff24');
            if (svgIcon) {
                // 更改SVG类名
                svgIcon.classList.remove('ZDI--RadioButtonOff24');
                svgIcon.classList.add('ZDI--RadioButtonOn24');

                // 添加新的路径
                const newPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
                newPath.setAttribute("d", "M18 12a6 6 0 1 1-12 0 6 6 0 0 1 12 0Z");
                svgIcon.appendChild(newPath);

                console.log('SVG icon updated');
            } else {
                console.error('SVG icon not found');
            }

            // 设置输入框的状态
            const input = radioButton.querySelector('.RadioButton-input');
            if (input) {
                input.checked = true;
                console.log('Input checked');
            } else {
                console.error('Input element not found');
            }

            console.log('状态已转换为改变后的状态');
        } else {
            console.error('Radio Button not found');
        }
    } else {
        console.error('Radio Labels not found');
    }
}, 5000);

