// function item_sz(img_el)
// {
//   var w = img_el.naturalWidth;
//   var h = img_el.naturalHeight;
//   var div_w = document.getElementsByClassName("item")[0].offsetWidth;

//   var div_h = h * div_w / w;

//   return div_h;
// }


// function reshape(elems)
// {
//   //Shape the size of each elemnt to be displayed
//   console.log("Resaphing "+elems.length);

//   var chOrd = null;
//   for(var i = 0; i < elems.length; i++) {
//       var spanTag = elems[i].children[0];

//       // Find the index of img child
//       if (chOrd === null)
//       {
//         for (chOrd=0; chOrd < spanTag.children.length && spanTag.children[chOrd].tagName !=='IMG'; chOrd++) {}
//       }
//       console.log("Test else "+chOrd);  

//       var eImg = spanTag.children[chOrd];      
//       var imgRatio = Number((eImg.naturalWidth / eImg.naturalHeight).toFixed(1)); //width to height ratio

//       if (imgRatio <= 0.7)
//       {
//         elems[i].className = "hvr-grow item L07"
//       }
//       else if (imgRatio <= 0.8)
//       {
//         elems[i].className = "hvr-grow item L08"
//       }
//       else if (imgRatio <= 1)
//       {
//         elems[i].className = "hvr-grow item L10"
//       }
//       else if (imgRatio <= 1.2)
//       {
//         elems[i].className = "hvr-grow item L12" 
//       }
//       else if (imgRatio <= 1.4)
//       {
//         elems[i].className = "hvr-grow item L14" 
//       }
//       else
//       {
//         elems[i].className = "hvr-grow item L16" 
//       }

//       if (i<10)
//         console.log("Cl " +elems[i].className);
//     }
// }



// ************************ UTIL ************************************

//Find the closest parent of specified class finder - will return null if no such element has been found
function findParent (el, cls) 
{
  while (el && !el.classList.contains(cls)) { el = el.parentElement;}
  return el;
}


function bindClickListener(listenerFunc)
{
    //Binds a listener to the click on the masonry object

    var container = document.querySelector('#container');
    var msnry = Masonry.data( container );

    eventie.bind( container, 'click', listenerFunc);
}

function unbindClickListener(listenerFunc)
{
    //Uninds previously bound listener

    var container = document.querySelector('#container');
    var msnry = Masonry.data( container );

    eventie.unbind( container, 'click', listenerFunc);
}


// ************************ MASONRY LISTENERS *********************************

function deleteSingle()
{
    //Delete the item that has been clicked on 
    var container = document.querySelector('#container');
    var msnry = Masonry.data( container );

    console.log("Container "+ container.children[0].getAttribute("class"));
    var e = findParent(event.target, "item"); 

    if ( !e ) {
      return;
    }
    
    // container.style.opacity = 0;
    // remove clicked element
    msnry.remove( e );

    // relayout remaining item elements
    msnry.layout();

    // container.style.opacity = 1;
    
}

function deleteMultiple(attrName)
{
    //NOTE: current implementation only removes items from the feed that have already loaded!

    //Delete the item that has been clicked on and all other items that have the same value of the given attribute
    //that are listed by the same seller
    //When applied to ebay feed, attribute is "data-sellerid"

    var container = document.querySelector('#container');
    var msnry = Masonry.data( container );

    var clicked = findParent(event.target, "item"); //clicked item
    var items = document.getElementsByClassName("item");

    if ( !clicked ) {
      return;
    }
    
    var sellerID = clicked.getAttribute(attrName);

    //remove all items of this seller
    for (var i=0; i<items.length; i++)
    {
        var e = items[i];
        if (e.getAttribute("data-sellerid") === sellerID)
        {
            msnry.remove( e );
        }            
    }
    // relayout remaining item elements
    msnry.layout();
}

function deleteAllFromSeller()
{
  //Delete all items of this seller
  return deleteMultiple("data-sellerid");
};

function markItem()
{
    //Add tick mark to clicked element
    var itemEl = findParent(event.target, "item"); 
    var tickEl = itemEl.getElementsByClassName('tick')[0];

    
    if (tickEl.classList.contains("hidden"))
    {
      tickEl.className = tickEl.className.replace( /(?:^|\s)hidden(?!\S)/ , '' );
    }
    else
    {
        //Already ticked - hide the tick
        tickEl.classList.add("hidden");
    }
}

function toggleEffect(){
    
    // Toggling the size when item is clicked - NOT IN USE

    var container = document.querySelector('#container');
    var msnry = Masonry.data( container );

    //TOGGLE SIZE WHEN CLICKED (& show all buttons)
    eventie.bind(container, 'click', function( event ) {

      var e = event.target;
      console.log("Click click: "+event.target.tagName );
      if (event.target.tagName == 'IMG')
      {
        e = e.parentNode.parentNode;
      }
      else if(event.target.tagName == 'SPAN')
      {
        e = e.parentNode;
      }

      console.log("Element: "+e.tagName );
      // don't proceed if item was not clicked on
      if ( !classie.has( e, 'item' ) ) {
        return;
      }

      // var span_el = e.getElementsByTagName('span')[0];
      
      // change size of div item via special css class
      classie.toggle( e, 'selected' );

      // console.log("Debug "+e.querySelectorAll('p,a').length);

      // hide/show all the buttons
      for (var i=0; i< e.querySelectorAll('p,a').length; i++)
      {
        c = e.querySelectorAll('p,a')[i];

        if (classie.has( c, 'button' )){
            classie.toggle( c, 'hidden' );
        }
      }

      //prevent image resizing
      // classie.toggle( span_el, 'nonselect' );

      // trigger layout
      msnry.layout();
      });
}

// ************************ MODE BUTTON LISTENERS *************************

var editMode = null; //id of the button pressed
var tickImgSrc = null;

function terminateEdit()
{
    //Terminates currently selected mode

    //Look and feel
    var btn = document.getElementById(editMode);
    btn.className = btn.className.replace( /(?:^|\s)selected(?!\S)/ , '' ); //remove 'selected' portion in css class of the button

    var feedContainer = document.getElementById("container");
    feedContainer.className = feedContainer.className.replace( /(?:^|\s)edit(?!\S)/ , '' );

    var feedItems = document.getElementsByClassName("item");
    for (var i=0; i<feedItems.length; i++)
    {
      feedItems[i].className = feedItems[i].className.replace( /(?:^|\s)edit(?!\S)/ , '' );

      //Enable links to ebay items
      var itemUrlLink = feedItems[i].getElementsByTagName("a")[0];
      itemUrlLink.className = itemUrlLink.className.replace( /(?:^|\s)disabled(?!\S)/ , '' ); 
    }

    if (editMode === "ignore_items")
    {
      unbindClickListener(deleteSingle);
    }
    else if (editMode === "ignore_sellers")
    {
      unbindClickListener(deleteAllFromSeller);
    }
    else if (editMode === "price_drop")
    {
      unbindClickListener(markItem);
    }


    editMode = null;
}

function editModeItems(feedItems)
{
    //Adjust the display of items when edit mode is turned on
    if (editMode)
    {
      for (var i=0; i<feedItems.length; i++)
      {
        feedItems[i].classList.add("edit");
        var itemUrlLink = feedItems[i].getElementsByTagName("a")[0];
        itemUrlLink.classList.add("disabled");
      }
    }
}

function editBtnClick(event)
{
    //Listens to clicks on the mode buttons
    var editBtn = event.target;
    var editBtnId = editBtn.id;

    if (editMode)
    {
        var prevEdit = editMode;
        terminateEdit();

        if (prevEdit === editBtnId) 
        {
          return;
        }
    }
    
    //Change the look and feel of the newly selected button
    editMode = editBtn.id;
    editBtn.classList.add("selected");

    //Change the look and feel of feed background
    var feedContainer = document.getElementById("container");

    if (!feedContainer.classList.contains("edit"))
    {
      feedContainer.classList.add("edit");
    }

    //Change the look of each item in the container
    //Disable the link opening in new tab
    var feedItems = document.getElementsByClassName("item");
    editModeItems(feedItems);

    if (editMode === "ignore_items")
    {
      bindClickListener(deleteSingle);
    }
    else if (editMode === "ignore_sellers")
    {
      bindClickListener(deleteAllFromSeller);
    }
    else if (editMode === "price_drop")
    {
      bindClickListener(markItem);
    }

}

// ************************ INITIALIZATION METHODS *************************

function initEditButtons(tickImg)
{

    tickImgSrc = tickImg;
    var btns = document.getElementsByClassName("btn-feed-edit");
    for (var i=0; i<btns.length; i++)
    {
      var b = btns[i];
      b.addEventListener( 'click' , editBtnClick );
    }

}

function initMsnryFeed() {
  docReady( function() {
   var $container = $('#container');

   // $container.imagesLoaded(function(){
      $container.masonry({
        itemSelector: '.item',
        columnWidth: 300
      });
    // });
 });
}

function initInfScroll(){
    
    //Override validation function in the prototype - this enables feed to start loading even 
    // if original page contains no elements in the container -- additional prefill param needs to be set as well
    $.infinitescroll.prototype._validate = function (opts) 
    {
          for (var key in opts) {
              if (key.indexOf && key.indexOf('Selector') > -1 && $(opts[key]).length === 0) {
                  if (key==='itemSelector') continue;
                  this._debug('Your ' + key + ' found no elements.');
                  return false;
              }
          }
        return true;
    };

    var $container = $('#container');
    
    $container.infinitescroll({
      retryT: 2, //time delay between two successive attempts to add a new page (in case the previous try failed)
      prefill: true, 
      behavior: 'wait',
      navSelector  : '#page-nav',    // selector for the paged navigation 
      nextSelector : '#page-nav a',  // selector for the NEXT link (to page 2)
      itemSelector : '.item',     // selector for all items you'll retrieve
      loading: {
          finishedMsg: 'All searches loaded!',
          img: 'http://i.imgur.com/6RMhx.gif'
        }
      },
      // trigger Masonry as a callback
      function( newElements ) {

        //hide spinner 
        $('#spinner').fadeOut();

        // hide new items while they are loading
        var $newElems = $( newElements ).css({ opacity: 0 });
        // ensure that images load before adding to masonry layout
        $newElems.imagesLoaded(function(){

          editModeItems($newElems);

          // show elems now they're ready
          $newElems.animate({ opacity: 1 });
          $container.masonry( 'appended', $newElems, true ); 
        });
      }
    );

    //If not immediatelly available, wait for page to appear on server
    $.extend($.infinitescroll.prototype, {
        _error_wait: function (xhr) 
        {
            
            var opts = this.options;

            if (xhr === 'end')
            {
                //Override default 'end' behaviour - instead of exiting, simply retry to fetch the same page again after time delay
                var pausedPg = opts.state.currPage;

                var instance = this;
                var timeD = opts.retryT;

                //insert temporary pause and retry
                setTimeout(function() {
                    //retrying the same page again - otherwise it'll increment the counter and search for the next one
                    instance.options.state.currPage = instance.options.state.currPage -1; 
                    instance.retrieve();
                  }, 1000 * timeD);

                return;
            }

            //copy pasted from the generic method
            if (xhr !== 'destroy' && xhr !== 'end') {
                xhr = 'unknown';
            }

            this._debug('Error', xhr);

            if (xhr === 'end' || opts.state.isBeyondMaxPage) {
                //This is overriden too
                this._showdonemsg();
            }

            opts.state.isDone = true;
            opts.state.currPage = 1; // if you need to go back to this instance
            opts.state.isPaused = false;
            opts.state.isBeyondMaxPage = false;
            this._binding('unbind');
        }
    });
}


