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
let page = u.substring(1, u.length - 3);
$("#footer").text(page);
$("title").text(page + " - NotePaper");
$(".content").html(`<div class="md-loading-notice" style="
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
                        </div>`)
$.ajax({
    type: "GET",
    url: "/" + page + "?md_api",
    success: (t) => {
        text = t;
        let lines=text.split("\n");
        let count = 0;
        for (let [idx,line] of lines.entries()) {
            let areas = line.split('$');
            for (let [idx1, area] of areas.entries()) {
                if (idx1 % 2) {
                    areas[idx1] = `<span id="tex_${count}">${area}</span>`;
                    count += 1;
                }
            }
            lines[idx] = areas.join('');
        }
        text = lines.join("\n");
        $(".content").html(marked.parse(text));

        for (let i=0;i<count;i++) {
            let tex=$(`#tex_${i}`).text();
            try {
                katex.render(tex,document.getElementById(`tex_${i}`));
            }
            catch {
                console.log(`The No. ${i+1} TeX "${tex}" cannot be rendered due to a syntax error.`);
                $(`#tex_${i}`).html(`<span style="color: #ffd700;">Invalid TeX here. See the browser console for further information.</span>`);
            }
        }
    },
});