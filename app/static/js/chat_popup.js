$(function() {
  $(".chat-cta").click(function() {
    $('#popover-chat').addClass('animate');
    return false;
  });

  var loadCnt = 0;
  $('#popover-chat iframe').load(function() {
    ++loadCnt;
    if(loadCnt >= 2) {
    }
  });
  $('#popover-chat .close').click(function() {
    $('#popover-chat').removeClass('animate');
    return false;
  });
});