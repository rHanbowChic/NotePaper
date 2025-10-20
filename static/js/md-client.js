var $ = document.querySelector.bind(document);

var text;

marked.setOptions({
  pedantic: false,
  gfm: true,
  breaks: false,
  tables: true,
  sanitize: false,
  smartLists: true,
  smartypants: false,
  xhtml: false,
});

let u = decodeURIComponent(window.location.pathname);
let page;
if (window.location.pathname.startsWith("/v/")) {
    page = u.substring(3, u.length);
}
else {
    page = u.substring(1, u.length - 3);
}

$("#footer").innerText = page;
$("title").innerText = page + " - " + $("title").innerText;
$("div.content").innerHTML = `<div class="md-loading-notice" style="
                            width: inherit;
                            height: inherit;
                            display: flex;
                            flex-wrap: nowrap;
                            align-items: center;
                            justify-content: center;
                        ">
                                <p style="
                                    font-size: 10px;
                                    color: #777;
                                    font-style: oblique;
                                ">Waiting for AJAX response...</p>
                        </div>`;


(async () => {
  const raw = await fetch("/papyrus/markdown/" + page);
  let text = (await raw.json()).text;


    renderMd(text);
})();

window.renderMd = async function (text) {
    let lines = text.split("\n");
    let in_block = false;
    let block_content = "";
    let trash_idx = []
    for (let [idx, line] of lines.entries()) {
        if (line == '$$') {
            in_block = !in_block;
            if (in_block) trash_idx.push(idx);
            if (!in_block) {
                lines[idx] = `<span class="tex-block">${block_content}</span>`;
                block_content = "";
            }
            continue;
        }
        if (in_block) {
            block_content += (line + '\n');
            trash_idx.push(idx);
            continue;
        }

        let areas = line.split('$');
        for (let [idx1, area] of areas.entries()) {
            if (idx1 % 2) {
                areas[idx1] = `<span class="tex-block">${area}</span>`;
            }
        }
        lines[idx] = areas.join('');
    }
    for (let i; i = trash_idx.pop();) lines.splice(i, 1);

    text = lines.join("\n");
    $("div.content").innerHTML = marked.parse(text);

    let count = 1;
    for (let elem of document.getElementsByClassName("tex-block")) {
        let tex = elem.innerText;
        verify_result = verifyTex(tex);

        if (!verify_result.verified) {
            elem.innerHTML = `<span style="color: #ffd700;">${verify_result.message}</span>`;
        } else {
            try {
                katex.render(tex, elem);
            } catch {
                console.log(`The No. ${count} TeX "${tex}" cannot be rendered due to a syntax error.`);
                elem.innerHTML = `<span style="color: #ffd700;">Invalid TeX here. See the browser console for further information.</span>`;
            }
        }

        count += 1;
    }

    $(".print").innerHTML = $("div.content").innerHTML;
}


function verifyTex(tex) {
    if (tex.length > 1000) return {
        verified: false,
        message: "Invalid TeX: too long",
    }
    let nesting_count = 0;
    let over_nested = false;
    [...tex].some(c => {
        if (c === "{") nesting_count += 1;
        if (c === "}") nesting_count -= 1;
        if (nesting_count > 10) {
            over_nested = true;
            return true;
        }
    });
    if (over_nested) return {
        verified: false,
        message: "Invalid TeX: too many nested expressions"
    }
    return {
        verified: true,
        message: "Verified",
    }
}
