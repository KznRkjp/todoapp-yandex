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
	$('#id_trello_token').on( 'mouseenter mouseleave', function(){
		$(this).attr('title', 'Введенный вами токен может и будет использован в коварных целях').tooltip();
	});
	$('#id_trello_key').on( 'mouseenter mouseleave', function(){
		$(this).attr('title', 'Введенный вами  ключ без всякого сомнения будет передан третьим лицам').tooltip();
	});
});
