function toggleReturnFields () {
    if ($('#id_action_choice').length > 0) {
        var current_choice = $('#id_action_choice :selected').text();
        if(current_choice == 'Returned') {
            $('.return-fields').slideDown('fast');
        } else {
            $('.return-fields').hide();
        }
    }
}

$(function(){
    toggleReturnFields();
    $('#id_action_choice').change(toggleReturnFields);
}); 
