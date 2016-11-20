// BASE HTML NAVBAR #############################

$(document).ready(function() {   
            var sideslider = $('[data-toggle=collapse-side]');
            var sel = sideslider.attr('data-target');
            var sel2 = sideslider.attr('data-target-2');
            sideslider.click(function(event){
                $(sel).toggleClass('in');
                $(sel2).toggleClass('out');
            });
        });


// MODEL ##########################

$('#myModal').on('shown.bs.modal', function () {
  $('#myInput').focus()
})

// model for sign up //

