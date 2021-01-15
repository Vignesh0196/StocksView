from bokeh.models import CustomJS

def mouse_move(figure, label):  
    return CustomJS(args=dict(figure=figure, label=label), code="""
    
        label.text = Number(cb_obj.y).toFixed(2);
        label.x = (figure.x_range.max);
        label.y = cb_obj.y;
        
    """ )
    
def hover_updates(indicators, ds, defaults, figures, x_axis):
    return CustomJS(args=dict(indicators=indicators, ds=ds, defaults=defaults, figures=figures, x_axis=x_axis), code="""
  
        var index = cb_data.index['line_indices'];
        var date = new Date();
            
         Object.keys(figures).forEach(function(item){
            date = new Date(ds.data[x_axis][index]);
            date.setSeconds(date.getSeconds() - 19800)
            if(date != 'Invalid Date'){
                $('#'+figures[item]+'_'+x_axis).text(date);
            }
        });
         
        
        for(const [key, value] of Object.entries(defaults)){
            value.forEach(function(item){
                $('#'+item).text(ds.data[item][index]);
            });
        }
        
        for(const [key, value] of Object.entries(indicators)){
            Object.keys(value['columns']).forEach(function(item){
                var column = value['columns'][item];
                $('#'+column).text(ds.data[column][index]);
            });
        }

    """ )

    
def label_position_update(figure, label):
    return CustomJS(args=dict(figure=figure, label=label), code="""

        label.x = (figure.x_range.max);
        
    """ )
    
def wheel_zoom(figure, label):

    return CustomJS(args=dict(figure=figure, label=label), code="""
        
        label.y = cb_obj.y;
        
    """ )
    
def mouse_enter(figure, label):
    return CustomJS(args=dict(figure=figure, label=label), code="""
        
        label.visible = true;
        
    """ )
    
def mouse_leave(figure, label):
    return CustomJS(args=dict(figure=figure, label=label), code="""
        
        label.visible = false;
        
    """ )
    
def auto_scale_on_drag(figure, indicators, ds, xaxis, category, default=''):
    
    return CustomJS(args=dict(figure=figure, indicators=indicators, source=ds, xaxis=xaxis, category=category, columns=default), code="""
   
        clearTimeout(window._autoscale_timeout);
        var index = source.data[xaxis];
        var start = cb_obj.start;
        var end = cb_obj.end;
        var start_index;
        var end_index;

        for (var i=0; i < index.length; ++i) {
            if(index[i] >= start){ 
                start_index = i;
                break;
            }
        }
        for (var i = (index.length-1); i > 0 ; --i) {
            if(index[i] <= end){
                end_index = i;
                break;
            }
        }
        
        var min = [];
        var max = [];
        if(category == 'fig1'){
            Object.keys(columns).forEach(function(item){
                if(columns[item] != 'candle_stick_color'){
                    max.push(Math.max(...source.data[columns[item]].slice(start_index, end_index)));
                    min.push(Math.min(...source.data[columns[item]].slice(start_index, end_index)));
                
                }
            });
        }
        
        for(const [key, value] of Object.entries(indicators)){
            for(const [column_key, column] of Object.entries(value)){
                 Object.keys(column).forEach(function(item){
                    if(column[item].visible == true){
                        
                        max.push(Math.max(...source.data[column_key].slice(start_index, end_index)));
                        min.push(Math.min(...source.data[column_key].slice(start_index, end_index)));
                    }
                }); 
            }
        }
        
        var range_max = Math.max(...max);
        var range_min = Math.min(...min);
        var pad = (range_max - range_min) * 0.05;
 
        window._autoscale_timeout = setTimeout(function() {
            figure.y_range.start = range_min - pad;
            figure.y_range.end = range_max + pad;
        }, 10);
        
    """ )
    
def auto_scale_on_change(figure, renderers):
    
    return CustomJS(args=dict(figure=figure, renderers=renderers), code="""
     
        var y_range;
        y_range = figure.y_range;
        y_range.renderers = [];
        
        if(Array.isArray(renderers)){
            for (let r of renderers) {
                if (r.visible){
                    y_range.renderers.push(r);
                    
                }
            }
        }
    
        if (Bokeh.index[figure.id]) {
            Bokeh.index[figure.id].update_dataranges();
        }
    
    """)
    
#Global JS Callbacks
def auto_scale_all(figures, indicators, ds, default=''):
    
    return CustomJS(args=dict(figures=figures, indicators=indicators, source=ds, default_columns=default), code="""
        clearTimeout(window._autoscale_timeout);
    
        var index = source.data.Time;
        var start = cb_obj.start;
        var end = cb_obj.end;
        var start_index;
        var end_index;
        var range_max = {};
        var range_min = {};
        var pad = {};
        var avail = [];
       

        for (var i=0; i < index.length; ++i) {
            
            if(index[i] >= start){ 
                start_index = i;
                break;
            }
        }
        for (var i = (index.length-1); i > 0 ; --i) {
            
            if(index[i] <= end){
                end_index = i;
                break;
            }
        }
        
        var d_max = [];
        var d_min = [];
        Object.keys(default_columns).forEach(function(item){
            if(default_columns[item] != 'candle_stick_color'){
                d_max.push(Math.max(...source.data[default_columns[item]].slice(start_index, end_index)));
                d_min.push(Math.min(...source.data[default_columns[item]].slice(start_index, end_index)));
                
            }
        });
        
        if(d_max.length != 0)
            avail.push('fig1');
        
        
        for(const [key, value] of Object.entries(indicators)){
            var min = [];
            var max = [];
            var flag = 1;
            if(key == 'fig1'){
                max = d_max;
                min = d_min;
            }
               
            for(const [indicator, columns] of Object.entries(value)){
                for(const [column_key, column] of Object.entries(columns)){
                    Object.keys(column).forEach(function(item){
                        if(column[item].visible == true){
                            max.push(Math.max(...source.data[column_key].slice(start_index, end_index)));
                            min.push(Math.min(...source.data[column_key].slice(start_index, end_index)));
                            if(flag == 1){
                                avail.push(key);
                                flag = 0;
                            }
                        }
                    }); 
                }
            }
            range_max[key] = Math.max(...max);
            range_min[key] = Math.min(...min);
            pad[key] = (range_max[key] - range_min[key]) * 0.05;
        }

        window._autoscale_timeout = setTimeout(function() {
        
            Object.keys(figures).forEach(function(item){
                if(avail.includes(item)){
                    
                    figures[item].y_range.start = range_min[item] - pad[item];
                    figures[item].y_range.end = range_max[item] + pad[item];
                }
                
            });
            
        }, 10);
    
    """)
    
    
def widget_update(figure, widgets):
    
    return CustomJS(args=dict(figure=figure, widgets=widgets), code="""
        var max = figure.x_range.max;
        Object.keys(widgets).forEach(function(item){
            if(item != 'fig1')
                widgets[item]['y_hover_label'].x = max
        });
    """)
    