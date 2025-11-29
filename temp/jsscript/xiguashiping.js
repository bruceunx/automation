/*
* 西瓜视频*/

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

const fileInput = document.querySelector('.byte-upload.xigua-upload-video-trigger.upload-video-trigger-card.has-extra-content input[type="file"][accept=".mp4,.flv,.wmv,.avi,.mov,.dat,.asf,.rm,.rmvb,.ram,.mpg,.mpeg,.3gp,.m4v,.dvix,.dv,.mkv,.vob,.qt,.cpk,.fli,.flc,.mod,.ts,.webm,.m2ts,video/*"]');
const binaryData = base64ToBinary(base64String);
const blob = new Blob([binaryData], {type: 'video/mp4'});
const file = new File([blob], '测试视频.mp4', {type:'video/mp4'});
const fileList = new DataTransfer();
fileList.items.add(file);
fileInput.files = fileList.files;
const event = new Event('change', { bubbles: true });
fileInput.dispatchEvent(event);

