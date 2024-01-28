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
    }
    else {
        $.ajax({
            url: "?request_text",
            type: 'GET',
            success: function(text) {
                if ($textarea.val() == content) {
                    content = text;
                    $textarea.val(text)
                }
            }
        });
    }
    $(".print").text(content);
}, 1000);