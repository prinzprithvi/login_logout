$(function() {
  $('.direct-upload').each(function() {
    var form = $(this);

    form.fileupload({
      url: form.attr('action'),
      type: 'POST',
      acceptFileTypes: /(\.|\/)(tar)|(tar.gz)$/i,  // Allowed File Types
      autoUpload: true,
      dataType: 'xml', // This is really important as s3 gives us back the url of the file in a XML document
      add: function (event, data) {
        $.ajax({
          url: '/direct_upload/signed_urls',
          type: 'GET',
          dataType: 'json',
          data: {title: data.files[0].name}, // send the file name to the server so it can generate the key param
          async: false,
          success: function(data) {
            // Now that we have our data, we update the form so it contains all
            // the needed data to sign the request
            form.find('input[name=key]').val(data.key);
            form.find('input[name=policy]').val(data.policy);
            form.find('input[name=signature]').val(data.signature);
          }
        });
        data.submit();
      },
      send: function(e, data) {
        $('.progress').fadeIn();
      },
      progress: function(e, data) {
        // This is what makes everything really cool, thanks to that callback
        // you can now update the progress bar based on the upload progress
        var percent = Math.round((e.loaded / e.total) * 100);
        $('.bar').css('width', percent + '%');
      },
      fail: function(e, data) {
          smoke.signal("upload failed", function(e){
          }, {
              duration: 2000,
              classname: "custom-class"
          });
      },
      success: function(data) {
        console.log('Success!');

        // Here we get the file url on s3 in an xml doc
        var url = decodeURIComponent($(data).find('Location').text());

          /*
           <?xml version="1.0" encoding="UTF-8"?>
           <PostResponse>
           <Location>http://cloudrive-uploads.s3.amazonaws.com/d48a1a4517f04261b51a15720a8fba44.bin</Location>
           <Bucket>cloudrive-uploads</Bucket>
           <Key>d48a1a4517f04261b51a15720a8fba44.bin</Key>
           <ETag>"7e4810aab8998785fd0700e1505a1967"</ETag>
           </PostResponse>

           */
          $.ajax({
              type:'POST',
              url:'/direct_upload/add_to_queue',
              data: JSON.stringify({location: $(data).find("Location").text(),
                  s3_bucket_name:$(data).find("Bucket").text(),
                  s3_key:$(data).find("Key").text(),
                  etag:$(data).find("ETag").text(),
                  current_bucket_id :bucket_id}),
              contentType:'application/json; charset=utf-16',
              dataType:'json',
              success:function (resp) {
                  console.log(resp);
              }
          });
          notify('Upload Notification', 'File sucessfully updated', {
              groupSimilar: false
          });
          return log("file upload done");
      },
      done: function (event, data) {
        $('.progress').fadeOut(300, function() {
          $('.bar').css('width', 0);
        });
      }
    });
  });
});
