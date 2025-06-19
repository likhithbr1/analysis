import React, { useState, useEffect } from 'react';
import axios from 'axios';
import clsx from 'clsx';
import Plot from 'react-plotly.js';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from 'recharts';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, TrendingUp } from 'lucide-react';

const TrendAnalysis = () => {
  const [summaryData, setSummaryData] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [sourceSystem, setSourceSystem] = useState('eon');

  const fetchSummary = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/analysis/summary', {
        source_system: sourceSystem,
        analysis_type: 'trend_analysis'
      });
      setSummaryData(response.data);
    } catch (error) {
      console.error('Error fetching summary:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDetail = async (product, range) => {
    setIsDetailLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/analysis/detail', {
        source_system: sourceSystem,
        analysis_type: 'trend_analysis',
        product,
        time_range: range
      });
      setDetailData(response.data);
    } catch (error) {
      console.error('Error fetching detail:', error);
    } finally {
      setIsDetailLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, [sourceSystem]);

  const handleProductClick = (product) => {
    setSelectedProduct(product);
    fetchDetail(product, '1m');
  };

  const handleTimeRangeChange = (range) => {
    if (selectedProduct) {
      fetchDetail(selectedProduct, range);
    }
  };

  const renderSparkline = (data, color) => (
    <div className="h-10 w-full">
      <Plot
        data={[{
          x: data.map(d => d.date),
          y: data.map(d => d.total_orders),
          type: 'scatter',
          mode: 'lines',
          line: { color, width: 2 },
          hoverinfo: 'skip'
        }]}
        layout={{
          margin: { l: 0, r: 0, t: 0, b: 0 },
          xaxis: { visible: false },
          yaxis: { visible: false },
          height: 40,
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent'
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '100%' }}
        key={`sparkline-${Date.now()}`}
      />
    </div>
  );

  const filteredData = summaryData.filter(item =>
    item.product.toLowerCase().includes(search.toLowerCase())
  );

  const containerClasses = "bg-background p-4 space-y-4 min-h-screen";

  if (selectedProduct && detailData) {
    return (
      <div className={containerClasses}>
        <div className="mb-4">
          <h1 className="text-4xl font-bold">📈 Product Sales Trend Dashboard</h1>
        </div>

        <div className="space-y-3">
          <h2 className="text-2xl font-semibold">📊 Detailed View: {detailData.product}</h2>
          <Button
            variant="outline"
            onClick={() => {
              setSelectedProduct(null);
              setDetailData(null);
            }}
          >
            🔙 Back to All Products
          </Button>

          <Tabs defaultValue="1m" onValueChange={handleTimeRangeChange}>
            <TabsList className="grid w-full grid-cols-4 my-4">
              <TabsTrigger value="1w">1 Week</TabsTrigger>
              <TabsTrigger value="1m">1 Month</TabsTrigger>
              <TabsTrigger value="1y">1 Year</TabsTrigger>
              <TabsTrigger value="2y">2 Years</TabsTrigger>
            </TabsList>

            {['1w', '1m', '1y', '2y'].map((range) => (
              <TabsContent key={range} value={range}>
                {isDetailLoading ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="text-center space-y-2">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                      <p className="text-muted-foreground">Loading detailed analysis...</p>
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-gradient-to-br from-white to-blue-50 rounded-xl shadow-xl p-4">
                      <h3 className="text-lg font-bold text-blue-700 mb-2 flex items-center gap-2">
                        <TrendingUp className="h-5 w-5" />
                        Sales Trend vs Forecast
                      </h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={detailData.chart_data?.dates.map((date, i) => ({
                          date,
                          actual: detailData.chart_data?.actual[i],
                          forecast: detailData.chart_data?.forecast?.[i] || null
                        }))}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                          <XAxis dataKey="date" stroke="#6b7280" />
                          <YAxis stroke="#6b7280" />
                          <Tooltip contentStyle={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)' }} />
                          <Line type="monotone" dataKey="actual" name="Actual Sales" stroke="#3B82F6" strokeWidth={3} dot={{ r: 6 }} />
                          {detailData.chart_data?.forecast && (
                            <Line type="monotone" dataKey="forecast" name="Forecast" stroke="#8B5CF6" strokeDasharray="5 5" strokeWidth={2} dot={{ r: 4 }} />
                          )}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="bg-gradient-to-br from-white to-purple-50 rounded-xl shadow-xl p-4">
                      <h3 className="text-lg font-bold text-purple-700 mb-4 flex items-center gap-2">
                        <TrendingUp className="h-5 w-5" />
                        Performance Metrics
                      </h3>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center p-4 bg-white rounded-lg border border-gray-100">
                          <span className="font-medium text-gray-700">Total Sales</span>
                          <span className="text-2xl font-bold text-blue-700">{detailData.total_sales?.toLocaleString() || 0}</span>
                        </div>
                        <div className="flex justify-between items-center p-4 bg-white rounded-lg border border-gray-100">
                          <span className="font-medium text-gray-700">Avg Daily Sales</span>
                          <span className="text-2xl font-bold text-indigo-700">{detailData.avg_sales?.toLocaleString() || 0}</span>
                        </div>
                        <div className="flex justify-between items-center p-4 bg-white rounded-lg border border-gray-100">
                          <span className="font-medium text-gray-700">Trend</span>
                          <span className={clsx("text-md font-bold", detailData.trend_percent >= 0 ? "text-green-600" : "text-red-600")}>
                            {detailData.trend_description || 'N/A'} ({detailData.trend_percent?.toFixed(1)}%)
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </div>
    );
  }

  return (
    <div className={containerClasses}>
      <div className="mb-6">
        <h1 className="text-4xl font-bold">📈 Product Sales Trend Dashboard</h1>
      </div>

      <div className="mb-6">
        <label htmlFor="source-system-trend" className="block text-sm font-medium text-gray-700 mb-2">
          📡 Select Source System:
        </label>
        <select
          id="source-system-trend"
          value={sourceSystem}
          onChange={(e) => {
            setSourceSystem(e.target.value);
            setIsLoading(true);
            setSelectedProduct(null);
            setDetailData(null);
          }}
          className="block w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white"
        >
          <option value="eon">EON System</option>
          <option value="sdp">SDP System</option>
          <option value="orion">ORION System</option>
        </select>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">All Product Trends [1 month]</h2>
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search Product"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center space-y-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="text-muted-foreground">Loading product data...</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredData.map((item, index) => {
            const isSelected = selectedProduct === item.product;
            return (
              <div
                key={index}
                className={clsx(
                  "border rounded-lg p-4 cursor-pointer transition-shadow bg-white",
                  {
                    "ring-2 ring-primary bg-blue-50": isSelected,
                    "opacity-50": selectedProduct && !isSelected
                  }
                )}
                onClick={() => handleProductClick(item.product)}
              >
                <div className="truncate font-semibold text-base mb-1">{item.product}</div>
                <div className="text-sm text-muted-foreground mb-1">
                  📦 Total Sales: {item.total_sales?.toLocaleString() || 0}
                </div>
                <div className="text-sm font-medium mb-2">
                  {item.trend_icon} {item.trend_description} ({item.trend_percent.toFixed(1)}%)
                </div>
                {item.sparkline_data && renderSparkline(item.sparkline_data, item.color)}
              </div>
            );
          })}
        </div>
      )}

      {filteredData.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <h3 className="text-lg font-semibold mb-2">No products found</h3>
          <p className="text-muted-foreground">Try adjusting your search terms</p>
        </div>
      )}
    </div>
  );
};

export default TrendAnalysis;

