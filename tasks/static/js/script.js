$(document).ready(function () {
	$(document).on('click', '.checkbox', function() {
		if($(this).is(":checked")){
      $(this).parent().addClass('completed');
      uid = $(this).attr('data-uid');
      $.get("/tasks/complete/" + uid);
      location.reload();
    }
		else{
			$(this).parent().removeClass('completed');
			uid = $(this).attr('data-uid');
			$.get("/tasks/uncomplete/" + uid);
			location.reload();
		}

	});

	$(document).on('click', '.remove', function(){
		$(this).parent().remove();
	});

});
