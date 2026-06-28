$(function() {

  // Auto-focus the first field when the sign-up modal opens
  $('#myModal').on('shown.bs.modal', function() {
    $(this).find('input:first').focus();
  });

  // "Find buses near me" — uses real geolocation instead of a hardcoded spot
  $('.js-geolocation').on('click', function() {
    if (!('geolocation' in navigator)) {
      $('#result').html('<p>Your browser can\'t share your location.</p>');
      return;
    }
    $('#result').html('<p>finding your nearest stop&hellip; 🚌</p>');
    navigator.geolocation.getCurrentPosition(function(position) {
      var lat = position.coords.latitude;
      var lng = position.coords.longitude;
      $('#result').load('/stop_info?lat=' + lat + '&long=' + lng);
    }, function() {
      $('#result').html('<p>Couldn\'t get your location &mdash; check your browser permissions.</p>');
    });
  });

});
