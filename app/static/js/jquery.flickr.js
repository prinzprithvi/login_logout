/*****************************************
 * Flickr API (in jQuery)
 * version: 1.0 (02/23/2009)
 * written for jQuery 1.3.2
 * by Ryan Heath (http://rpheath.com)
 *****************************************/
(function($) {
  // core extensions
  $.extend({
    // determines if an object is empty
    // $.isEmpty({})             // => true
    // $.isEmpty({user: 'rph'})  // => false
    isEmpty: function(obj) {
      for (var i in obj) { return false }
      return true
    }
  })
  
  // base flickr object
  $.flickr = {
    // the actual request url
    // (constructs extra params as they come in)
    url: function(method, params) {
      return 'http://api.flickr.com/services/rest/?method=' + method + '&format=json' +
        '&api_key=' + $.flickr.settings.api_key + ($.isEmpty(params) ? '' : '&' + $.param(params)) + '&jsoncallback=?'
    },
    // translate plugin image sizes to flickr sizes
    translate: function(size) {
      switch(size) {
        case 'sq': return '_s' // square
        case 't' : return '_t' // thumbnail
        case 's' : return '_m' // small
        case 'm' : return ''   // medium
        default  : return ''   // medium
      }
    },
    // determines what to do with the links
    linkTag: function(text, photo, href) {
      if (href === undefined) href = ['http://www.flickr.com/photos', photo.owner, photo.id].join('/')      
      return '<a href="' + href + '" title="' + photo.title + '">' + text + '</a>'
    }
  }
  
  // helper methods for thumbnails
  $.flickr.thumbnail = {
    src: function(photo, size) {
      if (size === undefined) size = $.flickr.translate($.flickr.settings.thumbnail_size)
      return 'http://farm' + photo.farm + '.static.flickr.com/' + photo.server + 
        '/' + photo.id + '_' + photo.secret + size + '.jpg'
    },
    imageTag: function(image) {
      return '<img src="' + image.src + '" alt="' + image.alt + '" />'
    }
  }
  // accepts a series of photos and constructs
  // the thumbnails that link back to Flickr
  $.flickr.thumbnail.process = function(photos) {
        var thumbnails = $.map(photos.photo, function(photo) {
        var image = new Image(), html = '', href = undefined;

        image.src = $.flickr.thumbnail.src(photo);
        image.alt = photo.title;

        var size = $.flickr.settings.link_to_size;
        if (size != undefined && size.match(/sq|t|s|m|o/))
            href = $.flickr.thumbnail.src(photo, $.flickr.translate(size));

        var data = {"bucket_id":$.flickr.settings.bucket_id,"file_data":$.flickr.thumbnail.src(photo,''),"size":'0',"content_type":'url'};
        var Info = "http://api.flickr.com/services/rest/?method=flickr.photos.getInfo";
        Info += "&api_key=" + $.flickr.settings.api_key;
        Info+= "&photo_id="+photo.id;
        Info += "&format=json";
        Info+= "&jsoncallback=?";
        $.ajax({
            type: 'GET',
            url: Info,
            context:data,
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function(resp) {
                console.log(resp)
                if(flickr_data != undefined && resp.stat =="ok"){
                    flickr_data.push(resp.photo);
                    console.log(resp.photo['id'])
                    $("#"+resp.photo['id']).html(resp.photo.description._content.substring(0, 100)+"...");
                }
            }
        });
        html = $.flickr.linkTag($.flickr.thumbnail.imageTag(image), photo, href)
        var titleHtml = photo.title
        return ['<tr><td><input type="checkbox" class="image_cb" onclick="javascript:flickr_image_handler(this);" value="'+photo.id+'"></td><td>' + html +'</td><td>'+titleHtml+ '</td><td id="'+photo.id+'"></td></tr>']
    }).join("\n")

    return thumbnails
  }
  
  // handles requesting and thumbnailing photos
  $.flickr.photos = function(method, options) {
    var options = $.extend($.flickr.settings, options || {}),
        elements = $.flickr.self, photos
    
    return elements.each(function() {
      $.getJSON($.flickr.url(method, options), function(data) {
        photos = (data.photos === undefined ? data.photoset : data.photos)
        elements.append($.flickr.thumbnail.process(photos))
      })
    })
  }
  
  // namespace to hold available API methods
  // note: options available to each method match that of Flickr's docs
  $.flickr.methods = {
    // http://www.flickr.com/services/api/flickr.photos.getRecent.html
    photosGetRecent: function(options) {
      $.flickr.photos('flickr.photos.getRecent', options)
    },
    // http://www.flickr.com/services/api/flickr.photos.getContactsPublicPhotos.html
    photosGetContactsPublicPhotos: function(options) {
      $.flickr.photos('flickr.photos.getContactsPublicPhotos', options)
    },
    // http://www.flickr.com/services/api/flickr.photos.search.html
    photosSearch: function(options) {
      $.flickr.photos('flickr.photos.search', options)
    },
    // http://www.flickr.com/services/api/flickr.photosets.getPhotos.html
    photosetsGetPhotos: function(options) {
      $.flickr.photos('flickr.photosets.getPhotos', options)
    }
  }
  
  // the plugin
  $.fn.flickr = function(options) {
    $.flickr.self = $(this)
    
    // base configuration
    $.flickr.settings = $.extend({
      api_key: '7151dd96d8a872a89a8f5766715f957e',
      thumbnail_size: 'sq'
    }, options || {})
    
    return $.flickr.methods
  }
})(jQuery);