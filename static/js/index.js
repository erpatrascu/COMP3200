
$(document).ready(function () {
  var trigger = $('.hamburger'),
     isClosed = false;

  trigger.click(function () {
      hamburger_cross();      
  });

  function hamburger_cross() {

    if (isClosed == true) {          
      trigger.removeClass('is-open');
      trigger.addClass('is-closed');
      isClosed = false;
    } else {   
      trigger.removeClass('is-closed');
      trigger.addClass('is-open');
      isClosed = true;
    }
  }

  //$( function() {
    $( "#datepicker" ).datepicker({ dateFormat: 'dd-mm-yy' }).datepicker("setDate", new Date());
  //} );

  $('[data-toggle="offcanvas"]').click(function () {
        $('#wrapper').toggleClass('toggled');
  });  

  $(".setbutton").click(function () {
    var date = $('#datepicker').datepicker().val();
    var shiftTime = $("#shift-select").val();
    var crimeType = $("#crime-select").val();
    console.log(date + "\n" + shift + "\n" + crime);

    $.ajax({
      type : "POST",
      url : "/set",
      data: JSON.stringify({ date: date, shiftTime: shiftTime, crimeType: crimeType }),
      contentType: 'application/json;charset=UTF-8',
    });
  })

});

