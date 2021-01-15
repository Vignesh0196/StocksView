import io
import json
import itertools
import pandas as pd
from jinja2 import Template
from functools import partial
from os.path import dirname, join
from collections import OrderedDict
import datetime as dt
import pdb

#Bokeh
from bokeh import events
from bokeh.io import curdoc
from bokeh.resources import CDN
from bokeh.embed import json_item
from bokeh.driving import linear
from bokeh.plotting import figure
from bokeh.models import ( ColumnDataSource, Select, CustomJS, 
                           CheckboxGroup, Slider, LinearAxis, Select,
                           Toggle, Label, Div, TextInput, DatetimeTickFormatter, 
                           Axis, Range1d, CrosshairTool, HoverTool, SaveTool, PanTool, WheelZoomTool, LassoSelectTool)
from bokeh.layouts import row, column, gridplot

#Custom Modules
from plot_utils import *
from custom_js import *

#Data Source
df_ = pd.read_csv(join(dirname(__file__), './copper.csv'))
df_['Time'] = pd.to_datetime(df_['Time'])
#df_['Time'] = pd.to_datetime(df_['Time'])+ dt.timedelta(0, -19800)
#df_['Time'] = pd.to_datetime(df_['Time']).dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
df_ = df_.fillna(df_.mean())
df = df_[30:]

df['candle_stick_color'] = ''
df.loc[df.Open > df.Close, 'candle_stick_color'] = 'red'
df.loc[df.Open < df.Close, 'candle_stick_color'] = 'green'

df1 = df[:150]
df2 = df[150:300]
live = df[150:]

df = df1

df = ColumnDataSource(df)
#Load Config File
with open(join(dirname(__file__),'./config.json')) as f:
  config = json.load(f)

#Figure Objects
figures = {}    

#Config Items
figures_list = [ _ for _ in config['figures']]


class Figure:
    def __init__(self, fig, config, ds, colors, parent_figure=None):
        
        self.name = fig
        self.config = config
        self.ds = ds
        self.category = config['figures'][self.name]['cat']
        self.defaults = {}
        self.colors = colors
        self.all_visible = False
        self.parent_figure = parent_figure

        self._indicators = {}
        self.indicators = {}
        self.indicator_properties = {}
        self.columns = []
        for _ in self.config['figures'][self.name]['indicators']:
            self._indicators[_] = config['indicators'][_]
            self.indicators[_] = {}
            self.indicator_properties[_] = {}
            self.columns += self._indicators[_]['columns']
        
        self._figure = config['figures'][fig]
        #self.figure = figure(y_axis_location='right', name=self.name, css_classes=['plot'])
        self.figure = figure(tools="pan,wheel_zoom,box_zoom,undo,redo,reset,crosshair", y_axis_location='right', name=self.name, css_classes=['plot'])
        self.widgets = {}
        #Default Renderer
        self.renderer = None

    def _line(self, x, y, color, alpha=1.0, ds=None, dashed=False):
        ds = self.ds if ds == None else ds
        return self.figure.line(x=x, y=y, line_width=2, source=ds, color=color, alpha=alpha, line_dash=('' if dashed==False else 'dashed'))

    def _vbar(self, x, y, color):
        return self.figure.vbar(x=x, top=y, width=0.9, source=self.ds, color=color)

    def _area(self, x, y, color):
        return self.figure.varea_stack(stackers=[y], x=x, source=self.ds, color=color, name='test')
        
    def _candle_stick(self, x0, x1, _open, _high, _low, _close, bar_color):
        prop = []
        prop.append( self.figure.segment(x0=x0, y0=_low, x1=x1, y1=_high, line_width=2, color='black', source=self.ds) )
        prop.append( self.figure.segment(x0=x0, y0=_open, x1=x1, y1=_close, line_width=6, color=bar_color, source=self.ds) )
        return prop

    def _graph_types(self, attr, old, new, key, column):    
        #Have to find the another for this if {}..else {}..
        if old == 'area':
            self.indicators[key][column][old][0].visible = False
        elif new == 'area':
            self.indicators[key][column][new][0].visible = True
        else:
            self.indicators[key][column][old].visible = False
            self.indicators[key][column][new].visible = True

    
    def _add_indicators(self):
        
        for key, items in self._indicators.items():
            #Visibility Reference
            self._indicators[key]['visible'] = False
            ###
            for column in items['columns']:
                _ = items['default_types'][ items['columns'].index(column) ]
                index = items['graph_types'].index(_)

                self.indicator_properties[key][column] = Select(value=items['graph_types'][index], options=items['graph_types'], id='select_'+column, name='select_'+column)
                self.indicator_properties[key][column].visible = False
                self.indicator_properties[key][column].on_change('value', partial(self._graph_types, key=key, column=column))

                self.indicators[key][column] = {}
                color = next(self.colors); 
                for graph in items['graph_types']:
                    
                    if graph == 'line':
                        self.indicators[key][column][graph] = self._line(self._figure['x_axis'], column, color)
                        self.indicators[key][column][graph].visible = False
                        if (items['graph_types'].index(graph)) == 0:
                            self.indicators[key][column][graph].name = column
                            
                    if graph == 'area':
                        self.indicators[key][column][graph] = self._area(self._figure['x_axis'], column, color)
                        self.indicators[key][column][graph][0].visible = False
                        if (items['graph_types'].index(graph)) == 0:
                            #self.indicators[key][column][graph].name = column
                            pass
                                      
                    if graph == 'bar':
                        self.indicators[key][column][graph] = self._vbar(self._figure['x_axis'], column, color)
                        self.indicators[key][column][graph].visible = False
                        if (items['graph_types'].index(graph)) == 0:
                            self.indicators[key][column][graph].name = column
                            
                    
    def _add_defaults(self):
        
        col = self._figure['columns']
        for graph in self._figure['graph_types']:
            color = next(self.colors)
            if graph == 'line':
                self.defaults[graph] = [self._line(self._figure['x_axis'], self._figure['default'][0], color)]
                self.defaults[graph][0].visible = self.all_visible
                
            elif graph == 'area':
                self.defaults[graph] = self._area(self._figure['x_axis'], self._figure['default'][0], color)
                self.defaults[graph][0].visible = self.all_visible
                
            elif graph == 'candle_stick':
                self.defaults[graph] = self._candle_stick(self._figure['x_axis'], self._figure['x_axis'], col[0], col[1], col[2], col[3], col[8])
                for item in self.defaults[graph]:
                    item.visible = self.all_visible
                    
            elif graph == 'heiken_ashi':
                self.defaults[graph] = self._candle_stick(self._figure['x_axis'], self._figure['x_axis'], col[4], col[5], col[3], col[7], col[8])
                for item in self.defaults[graph]:
                    item.visible = self.all_visible

    def show(self, indicator):
        for _, item in self.indicators[indicator].items():
            _type = self.indicator_properties[indicator][_].value
            self.indicator_properties[indicator][_].visible = True
            item[_type].visible = True
            
            #Visibility Reference
            self._indicators[indicator]['visible'] = True
            ###
    def hide(self, indicator):
        for _, item in self.indicators[indicator].items():
            _type = self.indicator_properties[indicator][_].value
            self.indicator_properties[indicator][_].visible = False
            item[_type].visible = False
            
            #Visibility Reference
            self._indicators[indicator]['visible'] = False
            ###
    def _add_widgets(self):
        self.widgets['y_hover_label'] = Label(x=(self.figure.x_range.end), y=(self.figure.y_range.start), text_font_size='12px', text='', text_color='white', text_alpha=0.9, text_baseline='bottom', text_align='left', background_fill_color='#999999', background_fill_alpha=1, angle_units='rad', render_mode='css', name='label')
            
        for key, item in self.widgets.items():
            self.figure.add_layout(item)

    def _add_events(self):
        self.figure.js_on_event(events.MouseWheel, wheel_zoom(self.figure, self.widgets['y_hover_label']))
        self.figure.js_on_event(events.MouseMove, mouse_move(self.figure, self.widgets['y_hover_label']))
        if self.category == 'main':
            self.figure.x_range.js_on_change('start', label_position_update(self.figure, self.widgets['y_hover_label']))
            # auto_scale_on_drag callback for single figure.
            # , auto_scale_on_drag(self.figure, self.indicators, self.ds, self._figure['x_axis'], self.category, self._figure['columns'])
            for renderer in self.figure.renderers:
                renderer.js_on_change('visible', auto_scale_on_change(self.figure, self.figure.renderers))
        else:
            #self.figure.x_range.js_on_change('start', label_position_update(self.figure, self.widgets['y_hover_label']))
            for renderer in self.figure.renderers:
                renderer.js_on_change('visible', auto_scale_on_change(self.figure, self.figure.renderers))
    
            
        self.figure.js_on_event(events.MouseEnter, mouse_enter(self.figure, self.widgets['y_hover_label']))
        self.figure.js_on_event(events.MouseLeave, mouse_leave(self.figure, self.widgets['y_hover_label'])) 

    def _update_y_range(self):
        _ = [ value['columns'] for key, value in self._indicators.items()]
        columns = list(itertools.chain.from_iterable(_))
        #Have to find other way for this line ...
        df = pd.DataFrame(self.ds.data)[-200:]
        ###
        y_max = df[columns].max().max()
        y_min = df[columns].min().min()
        pad = (y_max - y_min) * 0.05
        self.figure.y_range.start = (y_max + pad)
        self.figure.y_range.start = (y_min - pad)

    def _init_configuration(self):
        self.figure.xaxis.formatter=DatetimeTickFormatter(days=['%b %d'])
        self.figure.x_range.start = self.ds.data[self._figure['x_axis']][-150]
        self.figure.x_range.end = self.ds.data[self._figure['x_axis']][-1]
        #self.figure.x_range.follow_interval = 10000
        #self.figure.x_range.follow = "end"
        #self.figure.toolbar.active_scroll = 'auto'
        
        if self.name != 'fig1':
            self.figure.xaxis.visible = False

    def _annotations(self):
        columns = self._figure['annotations']
        self.an = {}
        for column in columns:
            color = 'black'
            x = self._figure['x_axis']
            self.an[column] = ColumnDataSource(data={x: [self.ds.data[x][0], self.ds.data[x][-1]] , column: [self.ds.data[column][-1], self.ds.data[column][-1]]})
            tmp = self._line(x, column, color=color, ds=self.an[column], dashed=True)
            
            
    def __call__(self):

        #Default Renderer
        self.renderer = self._line(self._figure['x_axis'], self.columns[0], 'black', alpha=0.0)

        if self.category == 'main':
            self._add_defaults()
            self.defaults['line'][0].visible = True
            #self._annotations()
        else:
            self.figure.visible = False

        #Adding Indicators
        self._add_indicators()
        self._update_y_range()

        #Figure_Widgets
        self._add_widgets()
        ###
        self._add_events()
        self._init_configuration()  

        self.figure.hover.tooltips = None
        
        #Tooltips
        #tooltip_columns = [(_, '@'+_+'{int.000}') for _ in self.columns] + [("Time", "@Time{%b %d - %H:%M:%S}")]
        #if self.category == 'main':
        #    tooltip_columns += [(_, '@'+_+'{int.000}') for _ in self._figure['columns'] if _ != 'candle_stick_color']
            
        
        


#__________________________________________________________        
         
#Initialize All Figures
x_range = None
color_gen = color_gen()
for fig in figures_list:
    if fig == 'fig1':
        figures[fig] = Figure(fig, config, df, color_gen)
    else:
        figures[fig] = Figure(fig, config, df, color_gen, figures['fig1'])
    figures[fig].__call__()
    
    if figures[fig].name == 'fig1':
        x_range = figures[fig].figure.x_range
    else:
        figures[fig].figure.x_range = x_range
    #Adding Widgets to Template
    for key, items in figures[fig]._indicators.items():
            [ curdoc().add_root(figures[fig].indicator_properties[key][column]) for column in items['columns'] ]

#Global Events
unwrapped_figures = {}
unwrapped_indicators = {}
unwrapped_widgets = {}
default_columns = figures['fig1']._figure['entities']
all_columns = []
for _, figure in figures.items():
    unwrapped_figures[_] = figure.figure
    unwrapped_indicators[_] = figure.indicators
    unwrapped_widgets[_] = {}
    unwrapped_widgets[_]['y_hover_label'] = figure.widgets['y_hover_label']
    all_columns += [ _ for _ in figure.columns]
    #Event_1
    [add_vlinked_crosshairs(figure.figure, fig.figure) for _, fig in figures.items()]
    #Event_2
    figure.figure.add_tools(HoverTool(tooltips=None, callback=hover_updates(config['indicators'], figure.ds, default_columns, figures_list, figure._figure['x_axis']), mode='vline', renderers=[figure.figure.renderers[0]]))
    
#Event_3
figures['fig1'].figure.x_range.js_on_change('start', auto_scale_all(unwrapped_figures, unwrapped_indicators, df, config['figures']['fig1']['columns']), widget_update(figures['fig1'].figure, unwrapped_widgets))
#df.js_on_change('data', auto_scale_all(unwrapped_figures, unwrapped_indicators, df, config['figures']['fig1']['columns']))

gp = gridplot([[figures[fig].figure] for fig in figures.keys()], sizing_mode='stretch_both', toolbar_location='below')
#self.figure.toolbar.active_scroll = self.figure.select_one(WheelZoomTool)
figures_stack = gp.children[0].children[0]

gp.name = 'gridplot'
### Adding to Template
curdoc().add_root(gp)
curdoc().template_variables['figures'] = config['figures']
curdoc().template_variables['indicators'] = config['indicators']
curdoc().template_variables['all_columns'] = all_columns

#for _, fig in figures.items():
#    gp = gridplot([[fig.figure]], sizing_mode='stretch_width')
#    gp.name = _+'_gp'   
#    curdoc().add_root(gp) 
    
#Graph Selection in Main Figure
_ = figures['fig1']._figure['graph_types']
select_graph = Select(value=_[0], options=_, name='graphs', css_classes=['select_button', 'selectpicker'], id='grphs')

def select_graph_callback(attr, old, new):
    for item in figures['fig1'].defaults[new]:
        item.visible = True
    for item in figures['fig1'].defaults[old]:
        item.visible = False
    
select_graph.on_change('value', select_graph_callback)    
### Adding to Template
curdoc().add_root(select_graph)

#Indicator Selection
all_indicators = [ _ for _ in config['indicators'] ]
select_indicator = CheckboxGroup(labels=all_indicators, active=[], name='indicators', id='indicators')

def select_indicator_callback(attr, old, new):

    xaxis_visible = ''
    active = [all_indicators[_] for _ in new]
    _new = diff(old, new)[0]    
    add_remove = all_indicators[_new]
    flag =  True if len(old) < len(new) else False
    for fig in figures_list:
        
        if len(intersection(figures[fig]._indicators, active)) != 0:
            figures[fig].figure.visible = True
            xaxis_visible = fig
            if add_remove in figures[fig]._indicators:
                if flag == True:
                    figures[fig].show(add_remove)
                    figures[fig].figure.xaxis.visible = True
                else:
                    figures[fig].hide(add_remove)
        else:
            if fig != 'fig1':
                figures[fig].figure.visible = False
                
            if add_remove in figures[fig]._indicators:
                if flag == False:
                    figures[fig].hide(add_remove)
        if fig != 'fig1':
            figures[fig].figure.xaxis.visible = False
                    
    if xaxis_visible != '':
        figures['fig1'].figure.xaxis.visible = False
        figures[xaxis_visible].figure.xaxis.visible = True
    else:
        figures['fig1'].figure.xaxis.visible = True
        

select_indicator.on_change('active', select_indicator_callback)
### Adding to Template
curdoc().add_root(select_indicator)

#tmp function
def instruments_selection(inst):
    if inst == 'Copper':
        tmp = dict(ColumnDataSource(df1).data)
    elif inst == 'Gold':
        tmp = dict(ColumnDataSource(df2).data)
    return tmp

#Instrument Selection
instruments_list = ['Copper', 'Gold']
instruments = Select(value=instruments_list[0], options=instruments_list, name='instruments', css_classes=['select_button', 'selectpicker'], id='inst')

def select_instruments_callback(attr, old, new):
    print(old, new)
    df.data = instruments_selection(new)
        

instruments.on_change('value', select_instruments_callback)

curdoc().add_root(instruments)


### Simulating tick data
df_ = live.rename(columns={'index': 'level_0'})
df_ = df_.reset_index()
N = len(df_)
def simulate_tick_data():
    for i in range(0, N):
        yield df_.iloc[i]

tick = simulate_tick_data()


@linear()
def stream(step):
    new_data = next(tick)
    df.stream(new_data)

curdoc().add_periodic_callback(stream, 500)




#testing

sizer = Slider(start=0.1, end=10, value=1, step=.1, title="size", name='sizer')

def sizing(plot, sizer):  
    return CustomJS(args=dict(plot=plot, sizer=sizer), code="""
        var height = plot.plot_height;
        var size = sizer.value*10
        
        $('#fig1').children().children().siblings().height((height+size));
        $('#fig1').children().height((height+size))
        $('#fig1').height((height+size))

    """ )


def resize(attr, old, new):
    print(old, new)
    #height = figures['fig1'].figure.plot_height
    #figures['fig1'].figure.plot_height = int(height*new)
    
sizer.on_change('value', resize)
#sizer.js_on_change('value', sizing(figures['fig1'].figure, sizer))

curdoc().add_root(sizer)
        
    
