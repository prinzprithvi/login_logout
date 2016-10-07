/*
 * jQuery File Upload Plugin JS Example 6.7
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/*jslint nomen: true, unparam: true, regexp: true */
/*global $, window, document */
var url = window.location.href;
var bucket_id =url.substring(url.lastIndexOf('/')+1);
$(function () {
    'use strict';
     // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload({'url':'/api/bucket/'+bucket_id+'/object/'});

    // Enable iframe cross-domain access via redirect option:
    $('#fileupload').fileupload(
        'option',
        'redirect',
        window.location.href.replace(
            /\/[^\/]*$/,
            '/cors/result.html?%s'
        )
    );
    $('#fileupload').fileupload({
        drop: function (e, data) {
            $.each(data.files, function (index, file) {
                $("#id_modal_upload_progress").modal('show');
            });
        },
        change: function (e, data) {
            $.each(data.files, function (index, file) {
                $("#id_modal_upload_progress").modal('show');
            });
        }
    });

	$('#fileupload').bind('fileuploadsubmit', function (e, data) {
    // The example input, doesn't have to be part of the upload form:
        eval('debugger;');
        console.log(data.files[0].name)
		data.formData = {'name':''+data.files[0].name};
	    if (!bucket_id) {
	      console.log('bucket_id is not set for some reason');
	      return false;
	    }
	});

    $('#fileupload').fileupload('option',{
        maxFileSize: 100000000,//total 100MB
        acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,
        maxNumberOfFiles: 1000,
        locale: {
            'File is too big': 'Datei ist zu groß',
            'File is too small': 'Datei ist zu klein',
            'Filetype not allowed': 'Dateityp nicht erlaubt',
            'Max number exceeded': 'Maximalanzahl überschritten'
        }
    });
    $('#fileupload').fileupload({
    // An array of image files that are to be resized:
    process: [
        {
            action: 'load',
            fileTypes: /^image\/(gif|jpeg|png)$/,
            maxFileSize: 100000000 // 20MB
        },
        {
            action: 'resize',
            maxWidth: 1440,
            maxHeight: 900,
            minWidth: 300,
            minHeight: 250
        },
        {
            action: 'save'
        }
    ]
    });
    //load_contents()
    $('#fileupload').bind('fileuploadprogressall', function (e, data) {
        // The example input, doesn't have to be part of the upload form:
        //load_contents()
        //expected to be written in loading template
    });
    // Upload server status check for browsers with CORS support:
    if ($.support.cors) {
        $.ajax({
            url: '/api/bucket/'+bucket_id+'/object/',
            type: 'HEAD'
        }).fail(function () {
            $('<span class="alert alert-error"/>')
                .text('Upload server currently unavailable - ' +
                        new Date())
                .appendTo('#fileupload');
        });
    }
    /*
     else {
        // Load existing files:
        $('#fileupload').each(function () {
            var that = this;
            $.getJSON(this.action, function (result) {
                if (result && result.length) {
                    $(that).fileupload('option', 'done')
                        .call(that, null, {result: result});
                }
            });
        });
    }
    */

});
