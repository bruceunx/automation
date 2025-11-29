/*
* b站图文 */

/*
* 输入标题内容 */
// 1.获取textarea元素
var textarea = document.querySelector('.iframe-comp-container iframe').
contentDocument.querySelector('textarea[placeholder="请输入标题（建议30字以内）"]');
// 2.设置textarea的值
textarea.value = '%s';
// 3.创建一个input事件并触发它
var event = new Event('input', {bubbles: true});
textarea.dispatchEvent(event);

/*
*输入正文内容 */
const editableDiv = document.querySelector('.iframe-comp-container iframe').
contentDocument.querySelector('.ql-editor');
if (editableDiv) {
console.log('Editable Div found:', editableDiv);
// 更新内容
editableDiv.innerHTML = '<p>%s</p>';
} else {
console.error('Editable Div not found');
}

/*
*提交 */
setTimeout(()=> {
    document.querySelector('.iframe-comp-container iframe').
        contentDocument.querySelector('.bre-btn.primary.size--large').click();
}, 3000);

