var feed_update_url;
var feed_terminate_url;
var log_url;

var running = false;
function start_feed_load(feed_load_url) 
{
    running = true;

    // send ajax POST request to start background job
    $.ajax({
        type: 'POST',
        url: feed_load_url,
        success: function(data, status, request) {
            console.log("url "+feed_update_url);

            feed_update_url = request.getResponseHeader('update_url');
            feed_terminate_url = request.getResponseHeader('terminate_url');
            log_url = request.getResponseHeader('log_url');
            update_progress(0);
        },
        error: function(smth, textStatus, errThrown) {
            
        }
    });
}

function exit_feed()
{
    running = false;

    $.ajax({
        type: 'GET',
        url: feed_terminate_url,
        success: function(data, status, request) {
              // feed_update_url = request.getResponseHeader('update_url');
              // update_progress(feed_update_url,0);
        },
        error: function(smth, textStatus, errThrown) {
            alert('Unexpected error: '+errThrown);
        }
    });

    //Log ignored sellers & items on the remote server
    logRemote(log_url);
}

function update_progress(pages_displayed) {

    if (!running)
        return;

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
                update_progress(pages_displayed);
            }, 2000);
        }
    });
}
