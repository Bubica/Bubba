
// Logs the time feed was generated on server
function init_time_log(time_log_url)
{
  $(document).ready(function(script_root){
    $("a#log").bind("click", function(){
      // $.getJSON($SCRIPT_ROOT + '/log_time');
      $.getJSON(time_log_url);
    });
  });
}

function init_seller_log(seller_log_url){
  // Logs seller to be ignored in the future feed
  $(document).ready(function(seller_log_url){
    $("a#ignore_seller").bind("click", function(){
      var sId = event.target.name;
      
      //Delete this item from the feed
      var masonTag = event.target.parentNode.parentNode;
      msnry_del_item(masonTag);

      //send the seller id to the server to be omitted from future feeds
      $.getJSON(seller_log_url, {sellerId: sId});

    });
  });
}
