//Local containers of ignored sellers and items
var ignoredSellersArr = [];
var ignoredItemsArr = [];

//Add selected elements ot local log
function logLocal_Seller(sellerId)
{
    ignoredSellersArr.push(sellerId);
}

function logLocal_Item(itemId, searchId)
{
    ignoredItemsArr.push([itemId, searchId]);
}

function logRemote(log_url)
{
    // Logs sellers and items to be ignored in the future feed
    // send ajax POST request log data
    // convert array of seller ids into single string 
    $.ajax({
        type: 'POST',
        url: log_url,
        data: {'sellers': ignoredSellersArr.join(), 'items': ignoredItemsArr.join(), 'last_search':lastDisplayedSearch()}, 
        success: function(data, status, request) {
          //All good
        },
        error: function(smth, textStatus, errThrown) {
            alert('Unexpected error: '+errThrown);
        }
    });
}
