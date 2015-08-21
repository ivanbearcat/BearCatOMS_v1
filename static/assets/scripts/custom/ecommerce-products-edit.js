var EcommerceProductsEdit = function () {

    var handleImages = function() {

        // see http://www.plupload.com/
        var uploader = new plupload.Uploader({
            runtimes : 'html5,flash,silverlight,html4',
             
            browse_button : document.getElementById('tab_images_uploader_pickfiles'), // you can pass in id...
            container: document.getElementById('tab_images_uploader_container'), // ... or DOM Element itself
             
            url : "/operationpost/operation",
             
            filters : {
                max_file_size : '10000mb',
                mime_types: [
                    {title : "Zip files", extensions : "zip,7z"}

                ]
            },
         
            // Flash settings
            flash_swf_url : 'assets/plugins/plupload/js/Moxie.swf',
     
            // Silverlight settings
            silverlight_xap_url : 'assets/plugins/plupload/js/Moxie.xap',             
            headers : {
                "X-CSRFToken":getCookie('_csrf_token')
            },
            init: {
                PostInit: function() {
                    $('#tab_images_uploader_filelist').html("");
         
                    $('#tab_images_uploader_uploadfiles').click(function() {
                        uploader.start();
                        return false;
                    });

                    $('#tab_images_uploader_filelist').on('click', '.added-files .remove', function(){
                        uploader.removeFile($(this).parent('.added-files').attr("id"));    
                        $(this).parent('.added-files').remove();                     
                    });
                },
         
                FilesAdded: function(up, files) {
                    plupload.each(files, function(file) {
                        $('#tab_images_uploader_filelist').append('<div class="alert alert-warning added-files" id="uploaded_file_' + file.id + '">' + file.name + '(' + plupload.formatSize(file.size) + ') <span class="status label label-info"></span>&nbsp;<a href="javascript:;" style="margin-top:-5px" class="remove pull-right btn btn-sm red"><i class="fa fa-times"></i> 移除</a></div>');
                    });
                },
         
                UploadProgress: function(up, file) {

                    $('#uploaded_file_' + file.id + ' > .status').html(file.percent + '%');
                },

                FileUploaded: function(up, file, response) {
                    var response = $.parseJSON(response.response);
                    if (response.code == 0) {
                        var id = response.id; // uploaded file's unique name. Here you can collect uploaded file names and submit an jax request to your server side script to process the uploaded files and update the images tabke

                        $('#uploaded_file_' + file.id + ' > .status').removeClass("label-info").addClass("label-success").html('<i class="fa fa-check"></i>'+response.msg); // set successfull operation
                        $('#tab_images_uploader_filelist').text("")
                        toastr.success(response.msg)
                        $('#datatables').dataTable().fnDraw()
                    } else {
                        $('#uploaded_file_' + file.id + ' > .status').removeClass("label-info").addClass("label-danger").html('<i class="fa fa-warning"></i>'+response.msg); // set failed operation
                        App.alert({type: 'danger', message: '文件上传失败，请重新上传', closeInSeconds: 10, icon: 'warning'});
                        toastr.error(response.msg)
                    }
                },
         
                Error: function(up, err) {
                    App.alert({type: 'danger', message: err.message, closeInSeconds: 10, icon: 'warning'});
                }
            }
        });

        uploader.init();

    }

    var handleReviews = function () {

        var grid = new Datatable();
        grid.init({
            src: $("#datatable_reviews"),
            dataTable: { // here you can define a typical datatable settings from http://datatables.net/usage/options 
                "aLengthMenu": [
                    [20, 50, 100, 150, -1],
                    [20, 50, 100, 150, "All"] // change per page values here
                ],
                "iDisplayLength": 20,
                "bServerSide": true,
                "sAjaxSource": "demo/ecommerce_product_reviews.php",
                "aoColumnDefs" : [{  // define columns sorting options(by default all columns are sortable extept the first checkbox column)
                    'bSortable' : true
                }],
                "aaSorting": [[ 0, "asc" ]] // set first column as a default sort by asc
            }
        });
    }

    var handleHistory = function () {

        var grid = new Datatable();
        grid.init({
            src: $("#datatable_history"),
            dataTable: { // here you can define a typical datatable settings from http://datatables.net/usage/options 
                "aLengthMenu": [
                    [20, 50, 100, 150, -1],
                    [20, 50, 100, 150, "All"] // change per page values here
                ],
                "iDisplayLength": 20,
                "bServerSide": true,
                "sAjaxSource": "demo/ecommerce_product_history.php",
                "aoColumnDefs" : [{  // define columns sorting options(by default all columns are sortable extept the first checkbox column)
                    'bSortable' : true
                }],
                "aaSorting": [[ 0, "asc" ]] // set first column as a default sort by asc
            }
        });
    } 

    var initComponents = function () {
        //init datepickers
        $('.date-picker').datepicker({
            rtl: App.isRTL(),
            autoclose: true
        });

        //init datetimepickers
        $(".datetime-picker").datetimepicker({
            isRTL: App.isRTL(),
            autoclose: true,
            todayBtn: true,
            pickerPosition: (App.isRTL() ? "bottom-right" : "bottom-left"),
            minuteStep: 10
        });

        //init maxlength handler
        $('.maxlength-handler').maxlength({
            limitReachedClass: "label label-danger",
            alwaysShow: true,
            threshold: 5
        });
    }

    var handlePlantForm = function() {

        // see http://www.plupload.com/
        var uploader = new plupload.Uploader({
            runtimes : 'html5,flash,silverlight,html4',

            browse_button : document.getElementById('tab_images_uploader_pickfiles'), // you can pass in id...
            container: document.getElementById('tab_images_uploader_container'), // ... or DOM Element itself

            url : "/operationpost/platformupload",

            filters : {
                max_file_size : '3000mb',
                mime_types: [
                    {title : "Zip files", extensions : "7z"}
                ]
            },

            // Flash settings
            flash_swf_url : 'assets/plugins/plupload/js/Moxie.swf',

            // Silverlight settings
            silverlight_xap_url : 'assets/plugins/plupload/js/Moxie.xap',
            headers : {
                "X-CSRFToken":getCookie('_csrf_token')
            },
            init: {
                PostInit: function() {
                    $('#tab_images_uploader_filelist').html("");

                    $('#tab_images_uploader_uploadfiles').click(function() {
                        uploader.start();
                        return false;
                    });

                    $('#tab_images_uploader_filelist').on('click', '.added-files .remove', function(){
                        uploader.removeFile($(this).parent('.added-files').attr("id"));
                        $(this).parent('.added-files').remove();
                    });
                },

                FilesAdded: function(up, files) {
                    plupload.each(files, function(file) {
                        $('#tab_images_uploader_filelist').append('<div class="alert alert-warning added-files" id="uploaded_file_' + file.id + '">' + file.name + '(' + plupload.formatSize(file.size) + ') <span class="status label label-info"></span>&nbsp;<a href="javascript:;" style="margin-top:-5px" class="remove pull-right btn btn-sm red"><i class="fa fa-times"></i> 移除</a></div>');
                    });
                },

                UploadProgress: function(up, file) {
                    $('#uploaded_file_' + file.id + ' > .status').html(file.percent + '%');
                },

                FileUploaded: function(up, file, response) {
                    var response = $.parseJSON(response.response);
                    if (response.code == 0) {
                        var id = response.id; // uploaded file's unique name. Here you can collect uploaded file names and submit an jax request to your server side script to process the uploaded files and update the images tabke

                        $('#uploaded_file_' + file.id + ' > .status').removeClass("label-info").addClass("label-success").html('<i class="fa fa-check"></i>'+response.msg); // set successfull operation
                        $('#tab_images_uploader_filelist').text("")
                        toastr.success(response.msg)
                        $('#datatables').dataTable().fnDraw()
                    } else {
                        $('#uploaded_file_' + file.id + ' > .status').removeClass("label-info").addClass("label-danger").html('<i class="fa fa-warning"></i>'+response.msg); // set failed operation
                        App.alert({type: 'danger', message: '文件上传失败，请重新上传', closeInSeconds: 10, icon: 'warning'});
                        toastr.error(response.msg)
                    }
                },

                Error: function(up, err) {
                    App.alert({type: 'danger', message: err.message, closeInSeconds: 10, icon: 'warning'});
                }
            }
        });

        uploader.init();

    }
    var handlePlantFormFormal = function() {

        // see http://www.plupload.com/
        var uploader = new plupload.Uploader({
            runtimes : 'html5,flash,silverlight,html4',

            browse_button : document.getElementById('tab_images_uploader_pickfiles'), // you can pass in id...
            container: document.getElementById('tab_images_uploader_container'), // ... or DOM Element itself

            url : "/operationpost/platformformalupload",

            filters : {
                max_file_size : '3000mb',
                mime_types: [
                    {title : "Zip files", extensions : "7z"}
                ]
            },

            // Flash settings
            flash_swf_url : 'assets/plugins/plupload/js/Moxie.swf',

            // Silverlight settings
            silverlight_xap_url : 'assets/plugins/plupload/js/Moxie.xap',
            headers : {
                "X-CSRFToken":getCookie('_csrf_token')
            },
            init: {
                PostInit: function() {
                    $('#tab_images_uploader_filelist').html("");

                    $('#tab_images_uploader_uploadfiles').click(function() {
                        uploader.start();
                        return false;
                    });

                    $('#tab_images_uploader_filelist').on('click', '.added-files .remove', function(){
                        uploader.removeFile($(this).parent('.added-files').attr("id"));
                        $(this).parent('.added-files').remove();
                    });
                },

                FilesAdded: function(up, files) {
                    plupload.each(files, function(file) {
                        $('#tab_images_uploader_filelist').append('<div class="alert alert-warning added-files" id="uploaded_file_' + file.id + '">' + file.name + '(' + plupload.formatSize(file.size) + ') <span class="status label label-info"></span>&nbsp;<a href="javascript:;" style="margin-top:-5px" class="remove pull-right btn btn-sm red"><i class="fa fa-times"></i> 移除</a></div>');
                    });
                },

                UploadProgress: function(up, file) {
                    $('#uploaded_file_' + file.id + ' > .status').html(file.percent + '%');
                },

                FileUploaded: function(up, file, response) {
                    var response = $.parseJSON(response.response);
                    if (response.code == 0) {
                        var id = response.id; // uploaded file's unique name. Here you can collect uploaded file names and submit an jax request to your server side script to process the uploaded files and update the images tabke

                        $('#uploaded_file_' + file.id + ' > .status').removeClass("label-info").addClass("label-success").html('<i class="fa fa-check"></i>'+response.msg); // set successfull operation
                        $('#tab_images_uploader_filelist').text("")
                        toastr.success(response.msg)
                        $('#datatables').dataTable().fnDraw()
                    } else {
                        $('#uploaded_file_' + file.id + ' > .status').removeClass("label-info").addClass("label-danger").html('<i class="fa fa-warning"></i>'+response.msg); // set failed operation
                        App.alert({type: 'danger', message: '文件上传失败，请重新上传', closeInSeconds: 10, icon: 'warning'});
                        toastr.error(response.msg)
                    }
                },

                Error: function(up, err) {
                    App.alert({type: 'danger', message: err.message, closeInSeconds: 10, icon: 'warning'});
                }
            }
        });

        uploader.init();

    }
    var handlePublish = function() {

        // see http://www.plupload.com/
        var uploader = new plupload.Uploader({
            runtimes : 'html5,flash,silverlight,html4',

            browse_button : document.getElementById('tab_images_uploader_pickfiles'), // you can pass in id...
            container: document.getElementById('tab_images_uploader_container'), // ... or DOM Element itself

            url : "/operationpost/installpublistupload",

            filters : {
                max_file_size : '3000mb',
                mime_types: [
                    {title : "Zip files", extensions : "7z"}
                ]
            },

            // Flash settings
            flash_swf_url : 'assets/plugins/plupload/js/Moxie.swf',

            // Silverlight settings
            silverlight_xap_url : 'assets/plugins/plupload/js/Moxie.xap',
            headers : {
                "X-CSRFToken":getCookie('_csrf_token')
            },
            init: {
                PostInit: function() {
                    $('#tab_images_uploader_filelist').html("");

                    $('#tab_images_uploader_uploadfiles').click(function() {
                        uploader.start();
                        return false;
                    });

                    $('#tab_images_uploader_filelist').on('click', '.added-files .remove', function(){
                        uploader.removeFile($(this).parent('.added-files').attr("id"));
                        $(this).parent('.added-files').remove();
                    });
                },

                FilesAdded: function(up, files) {
                    plupload.each(files, function(file) {
                        $('#tab_images_uploader_filelist').append('<div class="alert alert-warning added-files" id="uploaded_file_' + file.id + '">' + file.name + '(' + plupload.formatSize(file.size) + ') <span class="status label label-info"></span>&nbsp;<a href="javascript:;" style="margin-top:-5px" class="remove pull-right btn btn-sm red"><i class="fa fa-times"></i> 移除</a></div>');
                    });
                },

                UploadProgress: function(up, file) {
                    $('#uploaded_file_' + file.id + ' > .status').html(file.percent + '%');
                },

                FileUploaded: function(up, file, response) {
                    var response = $.parseJSON(response.response);
                    if (response.code == 0) {
                        var id = response.id; // uploaded file's unique name. Here you can collect uploaded file names and submit an jax request to your server side script to process the uploaded files and update the images tabke

                        $('#uploaded_file_' + file.id + ' > .status').removeClass("label-info").addClass("label-success").html('<i class="fa fa-check"></i>'+response.msg); // set successfull operation
                        $('#tab_images_uploader_filelist').text("")
                        toastr.success(response.msg)
                        $('#datatables').dataTable().fnDraw()
                    } else {
                        $('#uploaded_file_' + file.id + ' > .status').removeClass("label-info").addClass("label-danger").html('<i class="fa fa-warning"></i>'+response.msg); // set failed operation
                        App.alert({type: 'danger', message: '文件上传失败，请重新上传', closeInSeconds: 10, icon: 'warning'});
                        toastr.error(response.msg)
                    }
                },

                Error: function(up, err) {
                    App.alert({type: 'danger', message: err.message, closeInSeconds: 10, icon: 'warning'});
                }
            }
        });

        uploader.init();

    }
    return {

        //main function to initiate the module
        init: function () {
//            initComponents();

            handleImages();
//            handleReviews();
//            handleHistory();
        },
        plant_init: function () {
            handlePlantForm();
        },
        plant_formal_init: function(){
            handlePlantFormFormal();
        },
        install_publist_init: function(){
            handlePublish();
        }
    };

}();
