if (url_params.get('m') !== null || url_params.get('mono') !== null) {
    localStorage.setItem("np_prefer_mono", 1);
}
if (url_params.get('s') !== null || url_params.get('sans') !== null) {
    localStorage.removeItem("np_prefer_mono");
}
if (localStorage.getItem("np_prefer_mono")) {
    let mono_css = `<style>
        @font-face {
            font-family: 'JetBrains Mono';
            src:  url('/static/fonts/JetBrainsMono-Light.woff2') format('woff2');
        }
        textarea {
            font-family: 'JetBrains Mono', Consolas, 'Courier New', Courier, monospace;
            line-height: 1.5;
        }
        .content {
            font-size: 13px;
        }
    </style>`
    $("head").html($("head").html() + mono_css);
}