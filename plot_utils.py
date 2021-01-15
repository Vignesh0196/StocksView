from bokeh.models import CustomJS, CrosshairTool
from bokeh.palettes import Category20
import itertools
                           
#Vlinked Crosshair
def add_vlinked_crosshairs(fig1, fig2):
    js_move = '''if(cb_obj.x >= fig.x_range.start && cb_obj.x <= fig.x_range.end && cb_obj.y >= fig.y_range.start && cb_obj.y <= fig.y_range.end)
                    { cross.spans.height.computed_location = cb_obj.sx }
                 else 
                    { cross.spans.height.computed_location = null }'''
    js_leave = 'cross.spans.height.computed_location = null'
    
    cross1 = CrosshairTool()
    cross2 = CrosshairTool()
    fig1.add_tools(cross1)
    fig2.add_tools(cross2)
    fig1.add_tools(cross1)
    fig2.add_tools(cross2)
    args = {'cross': cross2, 'fig': fig1}
    fig1.js_on_event('mousemove', CustomJS(args = args, code = js_move))
    fig1.js_on_event('mouseleave', CustomJS(args = args, code = js_leave))
    args = {'cross': cross1, 'fig': fig2}
    fig2.js_on_event('mousemove', CustomJS(args = args, code = js_move))
    fig2.js_on_event('mouseleave', CustomJS(args = args, code = js_leave))
    
#Color Iterator
def color_gen():
    for c in itertools.cycle(Category20[20]):
        yield c 


#List1 - List2
def diff(li1, li2): 
    if len(li1) > len(li2):
        return (list(set(li1) - set(li2))) 
    else: 
        return (list(set(li2) - set(li1))) 
        
def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2)) 