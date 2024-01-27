var $textarea = $(".content");
var content = $textarea.val();
$(".print").text(content);
setInterval(function() {
    if (content !== $textarea.val()) {
        content = $textarea.val();
        $.ajax({
            type: "POST",
            data: "&t=" + encodeURIComponent(content)
        });
        $(".print").text(content);
    }
}, 1000);