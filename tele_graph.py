import pyqtgraph


class TelemetryGraph:
    def __init__ (self, graph, legend=False):
        self._graph = graph
        self._graph.setBackground('black')
        
        self.style = {'color': '#FFFFFF', 'font-size': '12px'}
        
        self.y_limit = 30
        
        self._x = dict()
        self._y = dict()
        self._lines = dict()
        self._pen = dict()
        
        if legend:
            self.graph.addLegend(offset=(0, 0))
            
            
    def addLine(self, name='default', color='white'):
        self._x[name] = [0]
        self._y[name] = [0]
        self._pen[name] = pyqtgraph.mkPen(color=color)
        self._lines[name] = self._graph.plot(self._x[name], self._y[name], name=name)
        
        
    def plotData(self, x, y, name='default'):
        self._x[name].append(x)
        self._y[name].append(y)
        
        if len(self._x[name]) >self.y_limit:
            self._x[name] = self._x[name][1:]
            self._y[name] = self._y[name][1:]
            
        self._lines[name].setData(self._y[name], self._x[name], name=name, pen=self._pen[name])
        
    def setBackground(self, color='w'):
        self._graph.setBackground(color)
        
    def setTitle(self, name, color = 'white'):
        self._graph.setTitle(name, color=color, size='12pt')
        
    def setYaxis(self, name):
        self._graph.setLable('left', name, **self.style)
        
    def setXaxis(self, name):
        self._graph.setLable('bottom', name, **self.style)
        