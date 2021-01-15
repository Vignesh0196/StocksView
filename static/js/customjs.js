
console.log("customjs.js loaded");
var last_checked = [];	

for(const [key, value] of Object.entries(figures)){
			
	value['indicators'].forEach(function(item){
		// $('<input id="color_'+item+'" type="button" class="jscolor btn btn-sm" onchange="color_update(this.jscolor, \''+item+'\')" value="">').appendTo('#test');
		
		 $(`<div id="modal_`+item+`" class="modal `+item+`_modal_sm" tabindex="-1" role="dialog" aria-labelledby="`+item+`_label" aria-hidden="true">
					 <div class="modal-dialog modal-sm">
					 <div class="modal-content">
						 
					 </div>
					 </div>
		 </div>`).appendTo('body');
		 
		indicators[item]['columns'].forEach(function(column){
			$('<input id="color_'+column+'" type="button" class="jscolor btn btn-sm" onchange="color_update(this.jscolor, \''+column+'\')" value="">').appendTo('#test');
		});

	 });
	

}


function add_bokeh_elements() {
	
		
      if(log_list.includes('Bokeh items were rendered successfully')){
		//Default Selections
		$('.bk-tool-icon-wheel-zoom')[0].click();
		
		
		//$('.plot').parent().attr('id', 'act');
		//$('.plot').each(function(){$(this).addClass('weighting_category')});
		$('.plot').each(function(index){$(this).attr('id', ('fig'+(index+1)))});
		//$('.plot').parent().parent().attr('id', 'activity');
		//$('.plot').parent().parent().addClass('weighting-category');
		
		// $('.plot').each(function(index){
			// $('<div id="cont_'+(index+1)+'" style="position: absolute"></div>').appendTo('#act');
			// $('#fig'+(index+1)).appendTo('#cont_'+(index+1));

		// });
		
		// $('<div id="coc" style="position: absolute"></div>').appendTo('#activity');
		// $('#act').appendTo('#coc');
		
		for(const [key, value] of Object.entries(figures)){
			$('<div id="'+key+'_container" style="position:absolute; top:5px; left:5px"></div>').appendTo('#'+key);
			
			$('<div id="'+key+'_'+value['x_axis']+'">('+value['x_axis']+')</div>').appendTo('#'+key+'_container');
			
			if(value['cat'] == 'main'){
				for(const [entity, columns] of Object.entries(value['entities'])){
					
					$('<div id="'+entity+'">('+entity+')</div>').appendTo('#'+key+'_container');
					
					// $('<span>&nbsp;&nbsp;</span>').appendTo('#'+entity);
					// $('<div id="'+entity+'">('+entity+')</div>').appendTo('#'+key+'_container');
					// $('<span>&nbsp;&nbsp;</span>').appendTo('#'+entity);

					columns.forEach(function(item){
						$('<span>&nbsp;&nbsp;</span>').appendTo('#'+entity);
						$('<span id="'+item+'"></span>').appendTo('#'+entity);
					});
				}
			}
			
			value['indicators'].forEach(function(item){
				$('<div id="'+item+'">('+item+')</div>').appendTo('#'+key+'_container');
				$('<span>&nbsp;&nbsp;</span>').appendTo('#'+item);
				$('<button type="button" class="btn btn-sm btn-outline-dark" data-toggle="modal" data-target=".'+item+'_modal_sm"><i class="fas fa-cog"></i></button>').appendTo('#'+item);
				$('<span>&nbsp;&nbsp;</span>').appendTo('#'+item);
				
				indicators[item]['columns'].forEach(function(column){

					var color = Bokeh.documents[0].get_model_by_name(column).glyph.attributes.line_color;
					$('<span>&nbsp;&nbsp;</span>').appendTo('#'+item);
					$('<span style="color:'+color+'" id="'+column+'"></span>').appendTo('#'+item);
					
					//__________________________
					
					$('<span>&nbsp;&nbsp;'+column+'&nbsp;:</span>').appendTo($('#modal_'+item).children().children());
					$('#select_'+column).wrap().appendTo($('#modal_'+item).children().children());
					$('#color_'+column).wrap().appendTo($('#modal_'+item).children().children());;
					$('#color_'+column).css('color', color);
					$('#color_'+column).css('background-color', color);
					
					Bokeh.documents[0].get_model_by_name('select_'+column).width = 200;
					Bokeh.documents[0].get_model_by_name('select_'+column).visible = true;
					console.log('#color_'+column);
					
				});
			});
		}
		
		clearInterval(callback);
		enable_resize();
	  }
}
var callback = setInterval(add_bokeh_elements, 1000);

//indicators selection
$('#checkbox_indicators').click(function(){
	var selected = [];
	$.each($("#checkbox_indicators input:checked"), function(){
		selected.push($(this).val());
	});

});

$('#checkbox_indicators').click(function(){
    var un_selected = [];
	$.each($("#checkbox_indicators input"), function(){
		un_selected.push($(this).val());
	});
});



//update color
function color_update(jscolor, item) {
	$('#'+item).css('color', '#'+jscolor);
	//$('#color_'+item).css('color', '#'+jscolor);
	Bokeh.documents[0].get_model_by_name(item).attributes.glyph.line_color = '#'+jscolor;
}


//change_line_size
function change_line_size(value, item){
	console.log(value);
	Bokeh.documents[0].get_model_by_name(item).attributes.glyph.line_width = parseFloat(value);
}

function change_line_style(value, item){
	if(value == 'Line'){
		Bokeh.documents[0].get_model_by_name(item).attributes.glyph.line_dash = [];
	}else if(value == 'Dotted'){
		Bokeh.documents[0].get_model_by_name(item).attributes.glyph.line_dash = [1, 5];
	}else if(value == 'Dashed'){
		Bokeh.documents[0].get_model_by_name(item).attributes.glyph.line_dash = [1, 5];
	}
}


function enable_resize(){
	console.log('enabling_resize');
	var percent = {}
    $('#act').resizable({
		minHeight: 0,	
		handles: 's',
		start: function(event, ui) {						
			
			orig_height = $(this).height();
			
			actheight1 = $('#activity').height();
		
			var ref = $(this);

			$('#act').children().each(function(index){
				percent[$(this).attr('id')] = ($(this).height() / ( actheight1 - ref.height() ))
			});
					
		},
		resize: function(event, ui) {
			
			if($(this).hasClass('zero') && $(this).height() > 5){
				$(this).removeClass('zero');
			}
			if(!$(this).hasClass('zero')){
				
				if($(this).height() > orig_height  || orig_height < (actheight1)) {
					
					var tmp = $(this);
					$('#act').children().each(function(index){
						if( tmp.attr('id') == $(this).attr('id')){
			
							$('#act').children().each(function(index){
								var curr = $(this);
								if( tmp.attr('id') != curr.attr('id') ){
									curr.height( (actheight1  -tmp.height()) * percent[curr.attr('id')]);
								}
							});
							
						}
					});
				
				} else {
					
					
					targetheight = $(this).height();
					$('#act .weighting-category').not(this).each(function(){
						$(this).height( (actheight2 - targetheight ) * 0.25);
						if($(this).hasClass('zero') && $(this).height() > 0){
							$(this).removeClass('zero');
						}
					})					
				}
			}
				
		},
		stop: function(event, ui) {	
			if($(this).height() == 0){
				$(this).addClass('zero');
			}
			totalheight = 0;
			$('#act > .weighting-category').each(function() {
				if(!$(this).hasClass('zero'))
				{
					totalheight += $(this).height();
				}
			});											
			
			actheight = 0;	
			$('#act .weighting-category').each(function(){				
				if(!$(this).hasClass('zero')){
					actheight += $(this).height();
				}
			})	
								
			actheight = 0;	
			$('#act .weighting-category').each(function(){				
				if(!$(this).hasClass('zero')){
					actheight += $(this).height();
				}
				if($(this).height() == 0 || $(this).hasClass('zero')){
					$(this).addClass('zero');
					
				}
			})	
			
						
			if($(this).height() >= actheight1)
			{
				$(this).animate({
					   height: (actheight1),
					 }, 500, function() {
				});
			}	
			
			
			$('#act .weighting-category').each(function(){
				if(!$(this).hasClass('zero')){
					thispercentage = $(this).height() / actheight;
					$(this).animate({
						   height: (actheight * thispercentage),
						 }, 500, function() {
					});
				}				
			})						
			
		}
	});
}




