# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.lib import colors
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.barcharts import HorizontalBarChart


class MyLineChartDrawing(Drawing):
    def __init__(self, width=600, height=400, *args, **kwargs):
        super(MyLineChartDrawing, self).__init__(width, height, *args, **kwargs)
        self.add(LinePlot(), name='chart')
        self.add(String(200, 180, 'Hello World'), name='title')
        # set any shapes, fonts, colors you want here.  We'll just
        # set a title font and place the chart within the drawing.
        # pick colors for all the lines, do as many as you need
        self.chart.x = 20
        self.chart.y = 30
        self.chart.width = self.width - 100
        self.chart.height = self.height - 75
        self.chart.lines[0].stroke_color = colors.blue
        self.chart.lines[1].stroke_color = colors.green
        self.chart.lines[2].stroke_color = colors.yellow
        self.chart.lines[3].stroke_color = colors.red
        self.chart.lines[4].stroke_color = colors.black
        self.chart.lines[5].stroke_color = colors.orange
        self.chart.lines[6].stroke_color = colors.cyan
        self.chart.lines[7].stroke_color = colors.magenta
        self.chart.lines[8].stroke_color = colors.brown

        self.chart.fillColor = colors.white
        self.title.fontName = 'Times-Roman'
        self.title.fontSize = 18
        self.chart.data = [((0, 50), (100, 100), (200, 200), (250, 210),
                            (300, 300), (400, 500))]
        self.chart.xValueAxis.labels.fontSize = 12
        self.chart.xValueAxis.forceZero = 0
        self.chart.xValueAxis.gridEnd = 115
        self.chart.xValueAxis.tickDown = 3
        self.chart.xValueAxis.visibleGrid = 1
        self.chart.yValueAxis.tickLeft = 3
        self.chart.yValueAxis.labels.fontName = 'Times-Roman'
        self.chart.yValueAxis.labels.fontSize = 12
        self.title.x = self.width / 2
        self.title.y = 0
        self.title.textAnchor = 'middle'
        self.add(Legend(), name='Legend')
        self.Legend.fontName = 'Times-Roman'
        self.Legend.fontSize = 12
        self.Legend.x = self.width
        self.Legend.y = 85
        self.Legend.dxTextSpace = 5
        self.Legend.dy = 5
        self.Legend.dx = 5
        self.Legend.deltay = 5
        self.Legend.alignment = 'right'
        self.add(Label(), name='XLabel')
        self.XLabel.fontName = 'Times-Roman'
        self.XLabel.fontSize = 12
        self.XLabel.x = 85
        self.XLabel.y = 5
        self.XLabel.textAnchor = 'middle'
        # self.XLabel.height = 20
        self.XLabel._text = ""
        self.add(Label(), name='YLabel')
        self.YLabel.fontName = 'Times-Roman'
        self.YLabel.fontSize = 12
        self.YLabel.x = 2
        self.YLabel.y = 80
        self.YLabel.angle = 90
        self.YLabel.textAnchor = 'middle'
        self.YLabel._text = ""
        self.chart.yValueAxis.forceZero = 1
        self.chart.xValueAxis.forceZero = 1


class MyBarChartDrawing(Drawing):
    def __init__(self, width=400, height=200, *args, **kw):
        Drawing.__init__(self, width, height, *args, **kw)
        self.add(HorizontalBarChart(), name='chart')
        self.add(String(200, 180, 'Hello World'), name='title')
        # set any shapes, fonts, colors you want here.  We'll just
        # set a title font and place the chart within the drawing
        self.chart.x = 20
        self.chart.y = 20
        self.chart.width = self.width - 20
        self.chart.height = self.height - 40

        self.title.fontName = 'Helvetica-Bold'
        self.title.fontSize = 12

        self.chart.data = [[100, 150, 200, 235]]


if __name__ == '__main__':
    # use the standard 'save' method to save barchart.gif, barchart.pdf etc
    # for quick feedback while working.
    MyBarChartDrawing().save(formats=['gif', 'png', 'jpg', 'pdf'], outDir='.',
        fnRoot='barchart')
