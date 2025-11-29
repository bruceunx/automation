/*
* 微博图文*/

/*
* 输入正文内容*/
// 1. 获取 textarea 元素
var textarea = document.querySelector('.Form_input_2gtXx');
// 2. 设置 textarea 的值
textarea.value = '生活中的美好往往就藏在这些看似平凡的瞬间！';
// 3. 创建一个 input 事件并触发它
var event = new Event('input', { bubbles: true });
textarea.dispatchEvent(event);

/*
*提交 */
setTimeout(()=> {
    document.querySelector('.woo-button-main.woo-button-flat.woo-button-primary.woo-button-m.woo-button-round.Tool_btn_2Eane').click();
}, 3000);
