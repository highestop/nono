// ==UserScript==
// @name         Bilibili 收藏页面取消滚动
// @match        https://space.bilibili.com/*/favlist
// @match        https://space.bilibili.com/*/favlist?*
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function () {
    'use strict';

    // 清理函数
    function cleanMaxHeight() {
        document.querySelectorAll('.fav-collapse-wrap').forEach(el => {
            // 直接删掉行内 max-height
            el.style.maxHeight = '';
            // 如果你想连 CSS 文件里的也覆盖，可加一行：
            el.style.setProperty('max-height', 'none', 'important');
        });
    }

    // 页面是 SPA，后续路由切换不会整页刷新，所以监听 DOM 变化
    const observer = new MutationObserver(() => cleanMaxHeight());
    observer.observe(document.body, {
        childList: true,
        subtree:   true
    });

    // 如果脚本管理器支持，离开页面时断开监听
    window.addEventListener('beforeunload', () => observer.disconnect());
})();