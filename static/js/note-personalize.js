var $ = document.querySelector.bind(document);
var url_params = new URLSearchParams(window.location.search);

const LIGHT_STYLES_OVERRIDE = `body {
    background: url(/static/img/bg.png) top left repeat #ebeef2;
}
.layer {
    background-color: #fff;
    border: 1px solid #ddd;
    box-shadow: 0 0 5px 0 #e4e4e4;
}
.content {
    background-color: #2a2a3a;
    color: #ddd;
}
.content {
    background-color: unset;
    color: #333;

}
.flag {
    color: #aaa;
}
a:link, a:visited, a:active {
    color: #aaa;
}
hr {
    border-color: unset;
}
input[type="button"] {
    background-color: rgba(85, 86, 88, 0.2);
    color: unset;
}
input[type="text"] {
    background-color: rgba(85, 86, 88, 0.15);
    color: unset;
}
@media (pointer: fine) {
    ::-webkit-scrollbar {
        width: 7px;
    }
    ::-webkit-scrollbar-thumb {
        background: #cecece;
    }
    ::-webkit-scrollbar:hover {
        background: unset;
    }
}`



const DARK_STYLES_OVERRIDE = `body {
    background: url(/static/img/bg-dark.png) top left repeat #1e1e1e;
}
.layer {
    background-color: #2a2a3a;
    border: 1px solid #484848;
    box-shadow: 0 0 5px 0 #0f0f14;
}
.content {
    background-color: #2a2a3a;
    color: #ddd;
}
.flag {
    color: #888;
}
a:link, a:visited, a:active {
    color: #888;
}
hr {
    border-color: #aaa;
}
input[type="button"], input[type="text"] {
    background-color: rgba(225, 225, 225, 0.25);
    color: #ddd;
}
::-webkit-scrollbar {
    background: #3b3b47;
}

::-webkit-scrollbar-thumb {
    background: #505059;
}

::-webkit-scrollbar:hover {
    background: #3f3f4b;
}
@media (pointer: fine) {
    ::-webkit-scrollbar {
        background: #3b3b47;
    }

    ::-webkit-scrollbar-thumb {
        background: #505059;
    }

    ::-webkit-scrollbar:hover {
        background: #3f3f4b;
    }
}`



const MONO_FONT_STYLES = `@font-face {
    font-family: 'JetBrains Mono';
    src:  url('/static/fonts/JetBrainsMono-Light.woff2') format('woff2');
}
textarea.content {
    font-family: 'JetBrains Mono', Consolas, 'Courier New', Courier, monospace;
    line-height: 1.5;
    font-size: 13px;
}
input[type="button"], input[type="text"] {
    background-color: rgba(225, 225, 225, 0.25);
    color: #ddd;
}`



if (url_params.get('m') !== null || url_params.get('mono') !== null) {
    localStorage.setItem("np_prefer_mono", 1);
}
if (url_params.get('s') !== null || url_params.get('sans') !== null) {
    localStorage.removeItem("np_prefer_mono");
}
if (localStorage.getItem("np_prefer_mono")) {
    $("head").innerHTML += `<style>${MONO_FONT_STYLES}</style>`;
}

if (url_params.get('light') !== null) {
    localStorage.setItem("np_theme", "light");
}
if (url_params.get('dark') !== null) {
    localStorage.setItem("np_theme", "dark");
}
if (url_params.get('reset-theme') !== null) {
    localStorage.removeItem("np_theme");
}
switch (localStorage.getItem("np_theme")) {
    case "light": $("head").innerHTML += `<style>${LIGHT_STYLES_OVERRIDE}</style>`; break;
    case "dark": $("head").innerHTML += `<style>${DARK_STYLES_OVERRIDE}</style>`; break;
}