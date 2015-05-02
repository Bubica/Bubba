function start_feed_load(feed_load_url) {
    // send ajax POST request to start background job
    $.ajax({
        type: 'POST',
        url: feed_load_url,
        success: function(data, status, request) {
            feed_update_url = request.getResponseHeader('Location');
            update_progress(feed_update_url,0);
        },
        error: function(smth, textStatus, errThrown) {
            alert('Unexpected error: '+errThrown);
        }
    });
}

function update_progress(feed_update_url, pages_displayed) {

    // send GET request to status URL on server - Client pushes for updates
    $.getJSON(feed_update_url, function(data) {
        // update UI
        var pgCnt = parseInt(data['pgCnt']);
        
        console.log("Page cnt: "+pgCnt+", previously: "+pages_displayed);
        pages_displayed = pgCnt;


        // Here we add to masonry new html pages...
        // Some tweaking of infinite scroll will be needed

        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('done' in data) {
                // FEED LOADED! FINISH AND EXIT
                
                
            }
            else {
                // something unexpected happened - ERROR
                
            }
        }
        else {
            // rerun in 10 seconds
            setTimeout(function() {
                update_progress(feed_update_url, pages_displayed);
            }, 2000);
        }
    });
}
