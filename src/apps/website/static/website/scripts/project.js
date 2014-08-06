/*
 * FIXED HEADER
 */
$('input[type="checkbox"]#smart-fixed-nav')
  .click(function () {
    if ($(this)
      .is(':checked')) {
      //checked
      $.root_.addClass("fixed-header");
    } else {
      //unchecked
      $('input[type="checkbox"]#smart-fixed-ribbon')
        .prop('checked', false);
      $('input[type="checkbox"]#smart-fixed-navigation')
        .prop('checked', false);

      $.root_.removeClass("fixed-header");
      $.root_.removeClass("fixed-navigation");
      $.root_.removeClass("fixed-ribbon");

    }
  });

/*
 * FIXED RIBBON
 */
$('input[type="checkbox"]#smart-fixed-ribbon')
  .click(function () {
    if ($(this)
      .is(':checked')) {
      //checked
      $('input[type="checkbox"]#smart-fixed-nav')
        .prop('checked', true);

      $.root_.addClass("fixed-header");
      $.root_.addClass("fixed-ribbon");

      $('input[type="checkbox"]#smart-fixed-container')
        .prop('checked', false);
      $.root_.removeClass("container");

    } else {
      //unchecked
      $('input[type="checkbox"]#smart-fixed-navigation')
        .prop('checked', false);
      $.root_.removeClass("fixed-ribbon");
      $.root_.removeClass("fixed-navigation");
    }
  });


/*
 * FIXED NAV
 */
$('input[type="checkbox"]#smart-fixed-navigation')
  .click(function () {
    if ($(this)
      .is(':checked')) {

      //checked
      $('input[type="checkbox"]#smart-fixed-nav')
        .prop('checked', true);
      $('input[type="checkbox"]#smart-fixed-ribbon')
        .prop('checked', true);

      //apply
      $.root_.addClass("fixed-header");
      $.root_.addClass("fixed-ribbon");
      $.root_.addClass("fixed-navigation");

      $('input[type="checkbox"]#smart-fixed-container')
        .prop('checked', false);
      $.root_.removeClass("container");

    } else {
      //unchecked
      $.root_.removeClass("fixed-navigation");
    }
  });

/*
 * RTL SUPPORT
 */
$('input[type="checkbox"]#smart-rtl')
  .click(function () {
    if ($(this)
      .is(':checked')) {

      //checked
      $.root_.addClass("smart-rtl");

    } else {
      //unchecked
      $.root_.removeClass("smart-rtl");
    }
  });


/*
 * INSIDE CONTAINER
 */
$('input[type="checkbox"]#smart-fixed-container')
  .click(function () {
    if ($(this)
      .is(':checked')) {
      //checked
      $.root_.addClass("container");

      $('input[type="checkbox"]#smart-fixed-ribbon')
        .prop('checked', false);
      $.root_.removeClass("fixed-ribbon");

      $('input[type="checkbox"]#smart-fixed-navigation')
        .prop('checked', false);
      $.root_.removeClass("fixed-navigation");

      if (smartbgimage) {
        $("#smart-bgimages")
          .append(smartbgimage)
          .fadeIn(1000);
        $("#smart-bgimages img")
          .bind("click", function () {
            $this = $(this);
            $html = $('html')
            bgurl = ($this.data("htmlbg-url"));
            $html.css("background-image", "url(" +
              bgurl + ")");
          })

        smartbgimage = null;
      } else {
        $("#smart-bgimages")
          .fadeIn(1000);
      }


    } else {
      //unchecked
      $.root_.removeClass("container");
      $("#smart-bgimages")
        .fadeOut();
      // console.log("container off");
    }
  });

/*
 * REFRESH WIDGET
 */
$("#reset-smart-widget")
  .bind("click", function () {
    $('#refresh')
      .click();
    return false;
  });

/*
 * STYLES
 */
$("#smart-styles > a")
  .bind("click", function () {
    $this = $(this);
    $logo = $("#logo img");
    $.root_.removeClassPrefix('smart-style')
      .addClass($this.attr("id"));
    $logo.attr('src', $this.data("skinlogo"));
    $("#smart-styles > a #skin-checked")
      .remove();
    $this.prepend(
      "<i class='fa fa-check fa-fw' id='skin-checked'></i>"
    );
  });

/**
 * BOOTSTRAP Hover Dropdown
 */
;(function ($, window, undefined) {
    // outside the scope of the jQuery plugin to
    // keep track of all dropdowns
    var $allDropdowns = $();

    // if instantlyCloseOthers is true, then it will instantly
    // shut other nav items when a new one is hovered over
    $.fn.dropdownHover = function (options) {
        // don't do anything if touch is supported
        // (plugin causes some issues on mobile)
        if('ontouchstart' in document) return this; // don't want to affect chaining

        // the element we really care about
        // is the dropdown-toggle's parent
        $allDropdowns = $allDropdowns.add(this.parent());

        return this.each(function () {
            var $this = $(this),
                $parent = $this.parent(),
                defaults = {
                    delay: 500,
                    instantlyCloseOthers: true
                },
                data = {
                    delay: $(this).data('delay'),
                    instantlyCloseOthers: $(this).data('close-others')
                },
                showEvent   = 'show.bs.dropdown',
                hideEvent   = 'hide.bs.dropdown',
                // shownEvent  = 'shown.bs.dropdown',
                // hiddenEvent = 'hidden.bs.dropdown',
                settings = $.extend(true, {}, defaults, options, data),
                timeout;

            $parent.hover(function (event) {
                // so a neighbor can't open the dropdown
                if(!$parent.hasClass('open') && !$this.is(event.target)) {
                    // stop this event, stop executing any code
                    // in this callback but continue to propagate
                    return true;
                }

                if(settings.instantlyCloseOthers === true)
                    $allDropdowns.removeClass('open');

                window.clearTimeout(timeout);
                $parent.addClass('open');
                $this.trigger(showEvent);
            }, function () {
                timeout = window.setTimeout(function () {
                    $parent.removeClass('open');
                    $this.trigger(hideEvent);
                }, settings.delay);
            });

            // this helps with button groups!
            $this.hover(function () {
                if(settings.instantlyCloseOthers === true)
                    $allDropdowns.removeClass('open');

                window.clearTimeout(timeout);
                $parent.addClass('open');
                $this.trigger(showEvent);
            });

            // handle submenus
            $parent.find('.dropdown-submenu').each(function (){
                var $this = $(this);
                var subTimeout;
                $this.hover(function () {
                    window.clearTimeout(subTimeout);
                    $this.children('.dropdown-menu').show();
                    // always close submenu siblings instantly
                    $this.siblings().children('.dropdown-menu').hide();
                }, function () {
                    var $submenu = $this.children('.dropdown-menu');
                    subTimeout = window.setTimeout(function () {
                        $submenu.hide();
                    }, settings.delay);
                });
            });
        });
    };

    $(document).ready(function () {
        // apply dropdownHover to all elements with the data-hover="dropdown" attribute
        $('[data-hover="dropdown"]').dropdownHover();

        $.validator.setDefaults({
          errorClass: "error",
          errorElement: "label",
          errorPlacement: function(error, element) {
            element.parent().append(error);
          }
        });
    });
})(jQuery, this);


/*-------------------------------------------------------------------------*/
/* Scroll to top
/*-------------------------------------------------------------------------*/

var $scrollTop = $(window).scrollTop();

//starting bind
if( $('#to-top').length > 0 && $(window).width() > 1020) {

  if($scrollTop > 350){
    $(window).bind('scroll',hideToTop);
  }
  else {
    $(window).bind('scroll',showToTop);
  }
}


function showToTop(){

  if( $scrollTop > 350 ){

    $('#to-top').stop(true,true).animate({
      'bottom' : '17px'
    },350,'easeInOutCubic');

    $(window).unbind('scroll',showToTop);
    $(window).bind('scroll',hideToTop);
  }

}

function hideToTop(){

  if( $scrollTop < 350 ){

    $('#to-top').stop(true,true).animate({
      'bottom' : '-30px'
    },350,'easeInOutCubic');

    $(window).unbind('scroll',hideToTop);
    $(window).bind('scroll',showToTop);

  }
}

//to top color
if( $('#to-top').length > 0 ) {

  var $windowHeight, $pageHeight, $footerHeight, $ctaHeight;

  function calcToTopColor(){
    $scrollTop = $(window).scrollTop();
    $windowHeight = $(window).height();
    $pageHeight = $('body').height();
    $footerHeight = $('#footer-outer').height();
    $ctaHeight = ($('#call-to-action').length > 0) ? $('#call-to-action').height() : 0;

    if( ($scrollTop-35 + $windowHeight) >= ($pageHeight - $footerHeight) && $('#boxed').length == 0){
      $('#to-top').addClass('dark');
    }

    else {
      $('#to-top').removeClass('dark');
    }
  }

  //calc on scroll
  $(window).scroll(calcToTopColor);

  //calc on resize
  $(window).resize(calcToTopColor);

}

//scroll up event
$('#to-top').click(function(){
  $('body,html').stop().animate({
    scrollTop:0
  },800,'easeOutCubic')
  return false;
});

