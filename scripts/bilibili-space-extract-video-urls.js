// ==UserScript==
// @name         Bilibili 视频列表页链接汇总
// @match        https://space.bilibili.com/*/upload/video
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function () {
    'use strict';
    
    window.extractVideoURLs = function () {
        const links = document.querySelectorAll('a.bili-cover-card[href]');
        const urls = [...new Set(
            Array.from(links).map(a => {
                const href = a.getAttribute('href').split('?')[0];
                return href.startsWith('//') ? 'https:' + href : href;
            })
        )];
        return urls;
    };
    
    console.log('[UserScript] window.extractVideoURLs() is ready.');
})();