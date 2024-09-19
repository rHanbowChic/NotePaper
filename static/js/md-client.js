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
            if (line.startsWith("$") && line.endsWith("$") && line.length < 500 && count < 50) {
                lines[idx]=`<span id="tex_${count}">${line}</span>`;
                count += 1;
            }
        }
        text = lines.join("\n");
        $(".content").html(marked.parse(text));

        for (let i=0;i<count;i++) {
            let tex=$(`#tex_${i}`).text();
            tex=tex.substring(1,tex.length-1);
            katex.render(tex,document.getElementById(`tex_${i}`));
        }
    },
});