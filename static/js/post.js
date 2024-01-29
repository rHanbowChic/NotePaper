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
            url: "?request_hash",
            type: 'GET',
            success: function(crc32_hash) {
                if (crc32(Utf8Encode($textarea.val())) != crc32_hash){
                    $.ajax({
                        url: "?request_text",
                        type: "GET",
                        success: function(text) {
                            if ($textarea.val() == content) {
                                $textarea.val(text);
                                content = text;
                            }
                        }
                    });
                }
            }
        });
    }
    $(".print").text(content);
}, 1000);