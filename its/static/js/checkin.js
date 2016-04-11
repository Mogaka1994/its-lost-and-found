$(document).ready(function () {

    $('#id_username').typeahead({
        minLength: 3,
        highlight: true
    }, {
        async: true,
        display: 'username',
        name: 'main',
        limit: 10,
        source: function source(query, syncCallback, asyncCallback) {
            var params = {query: query};
            $.getJSON(ITS.usersAutocompleteURL, params, function (data) {
                asyncCallback(data);
            });
        },
        templates: {
            notFound: '<div class="tt-suggestion not-found">No matching users found</div>',
            pending: '<div class="tt-suggestion">Searching for matching users...</div>',
            suggestion: function (context) {
                return ([
                    '<div>',
                        context.username,  ' - ',
                        context.full_name,  ' - ',
                        context.canonical_email_address,
                    '</div>'
                ].join(''));
            }
        }
    });

    $('#id_username').on('typeahead:select', function (event, suggestion) {
        $('#id_first_name').val(suggestion.first_name);
        $('#id_last_name').val(suggestion.last_name);
        $('#id_username').val(suggestion.username);
        $('#id_email').val(suggestion.canonical_email_address);
    });
    
    function togglePossibleOwnerFields () {
        if ($('#id_possible_owner_found').is(':checked')) {
            $('#possible-owner').slideDown('fast');
        } else {
            $('#possible-owner').slideUp('fast');
        }
    }

    $('#id_possible_owner_found').click(function () {
        togglePossibleOwnerFields();
    });
    
    togglePossibleOwnerFields();
});
