[![](https://github.com/Vignesh0196/StocksView/blob/main/stocksview__.jpg)](https://github.com/Vignesh0196/StocksView)
#  StocksView
## Real-Time Interactive Trading Data Visualization

### Features
* Convert your Excel into a Representative way with a Number of tools to interact with them in a single page
Dashboard
* Also connect you Real-Time data stream into the graphs using Stream() in main.py
* Add your own graphs with different Technical Indicators

### Demo
[![](https://github.com/Vignesh0196/StocksView/blob/main/Demo.gif)](https://github.com/Vignesh0196/StocksView)

### Requirements
    $ pip install -r requirements.txt

### Starting Application 
    $ bokeh serve stocksview
   
[![](https://github.com/Vignesh0196/StocksView/blob/main/starting_bokeh.png)](https://github.com/Vignesh0196/StocksView)
- Open your browser and paste this URL and Visualize your Data
- Connect you Real-Time Data stream in stream() function inside main.py

### Configuration
- Add your configuration in config.json
```python
"aroon": {
	"name": "aaron",
	"columns": ["aroonup", "aroondown"],
	"default_types": ["line", "line"],
	"graph_types": ["line", "bar", "area"]
}
```
- Code snippet to add a New Indicator called AROON
- Add this inside config.json under the Key called **indicators**
