/**
 * Created by rommelrico on 6/20/16.
 */

function showFlashMessage(message, time_ms) {
    var template = "<div class=\"container container-alert-flash\">\n" +
            "  <div class=\"row\">\n" +
            "    <div class=\"col-sm-3 col-sm-offset-8\">\n" +
            "      <div class=\"alert alert-success alert-dismissible\" role=\"alert\">\n" +
            "        <button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button>\n" +
            "        <span id=\"message-alert\">" + message + "</span>\n" +
            "      </div>\n" +
            "    </div>\n" +
            "  </div>\n" +
            "</div>\n";
    $("body").append(template);
    $(".container-alert-flash").fadeIn();
    setTimeout(function(){
        $(".container-alert-flash").fadeOut("normal", function(){
            $(this).remove();
        });
    }, time_ms);
}
