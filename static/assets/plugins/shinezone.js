function showAjaxLoad() {

//    $("#ajax_load").css("height", $(document).height());
//    $("#ajax_load").css("width", $(document).width());
//    $("#ajax_load").show();
    var  html = '<div class="loading-message ' +'"><img style="" src="../static/assets/img/loading-big.gif" align=""><span>&nbsp;&nbsp;'  + '</span></div>';
    $.blockUI({
        message: html,

        css: {
        border: '0',
        padding: '0',
        backgroundColor: 'none'
    }

    });}
function hideAjaxLoad() {
//    $("#ajax_load").toggle();
    $.unblockUI()
}
function isEmptyObject(obj) {
    for (var name in obj) {
        return false;
    }
    return true;
}

function guidGenerator() {
    var S4 = function() {
       return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    };
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}
function contain(Array, s) {
    for (var i = 0; i < Array.length; i++)
        if (Array[i] == s)
            return true;
    return false;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function export_excel(){
    var chart = $('#container1').highcharts()
    Highcharts.post('http://export.hcharts.cn/cvs.php', {
        csv: chart.getCSV()
      })
}
////全局的ajax访问，处理ajax清求时sesion超时
jQuery.ajaxSetup({
    crossDomain: false,
    contentType: "application/x-www-form-urlencoded;charset=utf-8",
    complete: function (XMLHttpRequest, textStatus) {
        if (XMLHttpRequest.responseText.indexOf("{\"redirect\":\"/login") >=0 &&  textStatus == 'error'){
            var next = XMLHttpRequest.responseText.split('next=')[1].split(',')[0]
            window.location.reload('/');
        }
    },
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('_csrf_token'));
        }
    }
});