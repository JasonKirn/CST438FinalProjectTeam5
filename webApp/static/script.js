$(document).ready(function() {

  $("#search").click(function() {
      console.log("First")
    var searchReq = $.get("/sendRequest/" + $("#query").val());
    searchReq.done(function(data) {
      console.log("Test")
      $("#url").attr("href", data.result);
    });
  });

});