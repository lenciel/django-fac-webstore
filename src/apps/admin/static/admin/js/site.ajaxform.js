//
//返回一个input的元素对应的Label的显示名字。
//
//比如下面的表单项:
//<label for="id_name">应用名称</label>
//<input class="required valid" id="id_name" maxlength="64" name="name" placeholder="应用名称，必填项" type="text">
//
//getInputLabelText($form, 'name') 返回 '应用名称'
//
function getInputLabelText($form, inputName) {
  var $label = $('label[for="id_'+inputName+'"]', $form);
  if ($label) {
    return $label.text();
  }

  // 如果找不到，尝试在不加再试一次
  $label = $('label[for="'+inputName+'"]', $form);
  if ($label) {
    return $label.text();
  }

  return inputName;
}

//
//格式化错误消息。
//
//response - JSON请求的响应
//
//只有 response['ret'] != 0 的时候才表示错误。
//
function formatResponseErrorMessage($form, response) {
  // e.g.
  // "ret": 1004
  if (response['ret'] == 0) {
    return null;
  }

  var errmsg = '';

  // e.g.
  // "errmsg-detail": {"id": ["系统不存在输入的应用ID"]}
  var errmsgDetail = response['errmsg-detail'];   // 包含各个字段的错误的更详细信息
  if (errmsgDetail) {
     errmsg += "<ul>";
     for (var fieldName in errmsgDetail) {
       errmsg += "<li>";
       errmsg += "<strong>" + getInputLabelText($form, fieldName) + "</strong>";
       errmsg += ": ";
       errmsg += errmsgDetail[fieldName];
       errmsg += "</li>";
     }
     errmsg += "</ul>";
  } else {
     // 如果没有详细的错误信息，使用errmsg字段来显示错误
     // e.g.
     // "errmsg": "验证表单失败，请确认表单的必填项都填写完整和数据格式正确"
     errmsg = response['errmsg'];
     if (response['detail']) {
         errmsg += "<h4>详细信息</h4>" + response['detail'];
     }
  }
  return errmsg;
}

// 表单提交错误时调用
function showFormSubmitError($form, errmsg) {
  var $alert = $('.alert', $form);
  console.log($alert);
  $alert.addClass('alert-warning').removeClass('alert-success');
  $alert.html('<h4>错误信息</h4> ' + errmsg);
  $alert.show();
}

//
//当表单返回错误时候调用这个函数来显示错误信息
//e.g.
//
// $form.ajaxForm({
//     dataType:  'json',
//     success:   function(response) {
//           if (response['ret'] == 0) {
//               showFormSubmitSuccess($form, '修改成功');
//           } else {
//               showFormErrorResponse($form, response);
//           }
//     }
// });
//
function showFormErrorResponse($form, response) {
  var errmsg = formatResponseErrorMessage($form, response);
  if (errmsg) {
    showFormSubmitError($form, errmsg);
  }
}

// 表单提交成功是调用
function showFormSubmitSuccess($form, msg, afterShowMessageCallback) {
  var $alert = $('.alert', $form);
  $alert.html('<h4>成功</h4> ' + msg);
  $alert.addClass('alert-success').removeClass('alert-warning');
  $alert.show();
  if (afterShowMessageCallback){
    afterShowMessageCallback();
  }
}

// 隐藏表单的提交信息，当表单内容改变时会自动调用
function hideFormSubmitMessage($form) {
  var $alert = $('.alert', $form);
  $alert.hide();
}

// 文本输入框长度限制提示
function input_limit_func() {
  var limit = parseInt($(this).attr('maxlength')) || parseInt($(this).attr('data-maxlength')) || 100;
  $(this).inputlimiter({
    "limit": limit,
    remText: '还可以输入%n字, ',
    limitText: '最多可以输入 : %n.'
  });
}

(function($){

  $.fn.enableAceFileInput = function (extendName) {
    this.ace_file_input({
      style: 'well',
      thumbnail: 'large',
      no_file: '无 ...',
      btn_choose: '选择文件(' + extendName + ')',
      btn_change: '修改',
      before_change: function (files, dropped) {
        var file = files[0];
        var file_name;
        if (typeof file == "string") {
          file_name = file;
        } else {
          file_name = file.name;
          if (file.size == 0) {
            file_name = "";
          }
        }
        var filter = new RegExp("\\.(" + extendName + ")$", "i");
        //file is just a file name here (in browsers that don't support FileReader API such as IE8)
        var is_valid = filter.test(file_name);
        if (!is_valid) {
          bootbox.dialog('请选择正确的文件 ' + file_name, [
            {"label": "确定"}
          ])
        }
        return is_valid;
      }
    });
  };

  $.fn.enableAceImageInput = function (maxWidth, maxHeight, minWidth, minHeight) {
    var extendName = "jpg|bmp|png|jpeg|gif"
    var ace_file_input = this.ace_file_input({
      style: 'well',
      thumbnail: 'large',
      no_file: '无 ...',
      btn_choose: '选择图片(' + extendName + ')',
      btn_change: '修改',
      before_change: function (files, dropped) {
        var file = files[0];
        var file_name;
        if (typeof file == "string") {
          file_name = file;
        } else {
          file_name = file.name;
          if (file.size == 0) {
            file_name = "";
          }
        }
        var filter = new RegExp("\\.(" + extendName + ")$", "i");
        //file is just a file name here (in browsers that don't support FileReader API such as IE8)
        var is_picture = filter.test(file_name);
        if (is_picture) {
          // check image size to avoid to exceed the max width and height
          var img = new Image();
          img.onload = function() {
            if ((maxWidth && this.width > maxWidth) || (maxHeight && this.height > maxHeight)) {
              bootbox.dialog('图片' + file_name +'尺寸 ' + this.width + 'x' + this.height + '超过了最大允许尺寸 ' + maxWidth + 'x' + maxHeight,
                  [{"label": "确定"}]);
              ace_file_input.data('ace_file_input').reset_input();
            }
            if ((minWidth && this.width < minWidth) || (minHeight && this.height < minHeight)) {
              bootbox.dialog('图片' + file_name +'尺寸 ' + this.width + 'x' + this.height + '不满足最小尺寸 ' + minWidth + 'x' + minHeight,
                  [{"label": "确定"}]);
              ace_file_input.data('ace_file_input').reset_input();
            }
          };
          var _URL = window.URL || window.webkitURL;
          img.src = _URL.createObjectURL(file);
        } else {
          bootbox.dialog('请选择正确的图片 ' + file_name, [{"label": "确定"}])
        }
        return is_picture;
      }
    });
  };

  $.fn.buildFormValidationRules = function (shouldFillPlaceholder) {
    var rules = [];
    var $form = this;
    $("input, textarea", $form).each(function () {
      var name = $(this).attr('name');
      var rule = {};

      if ($(this).hasClass("required")) {
        rule['required'] = true;
        // set the placeholder if has no value
        if (shouldFillPlaceholder && !$(this).attr('placeholder')) {
          var label = getInputLabelText($form, name);
          if (label) {
            $(this).attr('placeholder', $.trim(label) + " 必填");
          }
        }
      }
      if ($(this).attr('maxlength')) {
        rule['rangelength'] = [ 1, parseInt($(this).attr('maxlength'))];
        $(this).data().maxlength = $(this).attr('maxlength');
      }
      if ($(this).data('regex')) {
        rule['regex'] = $(this).data('regex');
      }
      if (Object.keys(rule).length > 0) {
        rules[name] = rule
      }
    });
    return rules;
  };

  $.fn.showServerResponseError = function (responseText, req, targetUrl) {
    var errmsg = '出错啦。';

    if (req.status) {
      errmsg = errmsg + '服务器状态码: ' + req.status + '。';
    }
    if (targetUrl) {
      errmsg += '目标页面: ' + targetUrl;
    }
    errmsg += '<pre>' + responseText + "</pre>";
    this.html('<div class="well well-large well-transparent lead">\
                  <i class="icon-warning-sign icon-2x pull-left"></i> ' + errmsg + '</div>');
  };

  $.fn.buildAjaxFormOptions = function(){
    var $form = this;
    return {
      dataType: 'json',
      beforeSubmit: function (formData, jqForm, options) {
        var is_valid = $form.valid();
        $(":submit", $form).attr("disabled", $form.valid());
        return is_valid
      },
      // success identifies the function to invoke when the server response
      // has been received
      success: function (response) {
        if (response['ret'] == 0) {
          showFormSubmitSuccess($form, '保存成功，正在返回!!!!', function () {
            window.history.go(-1);
          });
        } else {
          var commonMsg = response['errmsg-detail']['__all__'];
          if (commonMsg) {
            showFormSubmitError($form, commonMsg);
            delete response['errmsg-detail']['__all__'];
          }
          var validator = $form.validate();
          validator.showErrors(response['errmsg-detail']);
          $(":submit", $form).attr("disabled", false);
        }
      },

      error: function (xhr, textStatus, errorThrown) {
        $form.showServerResponseError(xhr.responseText, xhr, $form.attr('action'));
        $(":submit", $form).attr("disabled", false);
      }
    };
  };

  $.fn.enableChosen = function (options) {
    return this.chosen($.extend({no_results_text: '没有找到数据', search_contains: true}, options || {}));
  };

})(jQuery);
