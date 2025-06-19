import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const ProductComparison = () => {
  const [sourceSystem, setSourceSystem] = useState('eon');
  const [product1, setProduct1] = useState('');
  const [product2, setProduct2] = useState('');
  const [trendData1, setTrendData1] = useState(null);
  const [trendData2, setTrendData2] = useState(null);
  const [forecastData1, setForecastData1] = useState(null);
  const [forecastData2, setForecastData2] = useState(null);
  const [timeRange, setTimeRange] = useState('1m');
  const [loading, setLoading] = useState(false);

  const fetchTrendData = async (product, setter) => {
    try {
      const res = await axios.post('http://localhost:5000/analysis/detail', {
        source_system: sourceSystem,
        analysis_type: 'trend_analysis',
        product,
        time_range: timeRange
      });
      setter(res.data);
    } catch (err) {
      console.error(`Error fetching trend for ${product}`, err);
    }
  };

  const fetchForecastData = async (product, setter) => {
    try {
      const res = await axios.post('http://localhost:5000/forecast/detail', {
        source_system: sourceSystem,
        product,
      });
      setter(res.data);
    } catch (err) {
      console.error(`Error fetching forecast for ${product}`, err);
    }
  };

  useEffect(() => {
    if (product1) fetchTrendData(product1, setTrendData1);
    if (product2) fetchTrendData(product2, setTrendData2);
  }, [product1, product2, timeRange, sourceSystem]);

  useEffect(() => {
    if (product1) fetchForecastData(product1, setForecastData1);
    if (product2) fetchForecastData(product2, setForecastData2);
  }, [product1, product2, sourceSystem]);

  const renderTrendBlock = (data) => (
    <div className="border rounded-lg p-4 bg-white w-full">
      <h3 className="text-xl font-semibold mb-4">{data?.product} - Trend</h3>
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="text-sm text-muted-foreground">Total Sales</div>
          <div className="text-lg font-semibold">{data?.total_sales?.toLocaleString() || 0}</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-muted-foreground">Avg Daily Sales</div>
          <div className="text-lg font-semibold">{data?.avg_sales?.toLocaleString() || 0}</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-muted-foreground">Trend</div>
          <div className="text-lg font-semibold">{data?.trend_description || 'N/A'}</div>
          <div className={`text-sm ${data?.trend_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {data?.trend_percent ? `${data.trend_percent.toFixed(1)}%/day` : ''}
          </div>
        </div>
      </div>
      <Plot
        data={[{
          x: data?.chart_data?.dates || [],
          y: data?.chart_data?.actual || [],
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Orders',
          line: { color: data?.trend_percent < 0 ? 'red' : 'green', width: 2 }
        }]}
        layout={{
          xaxis: { title: 'Date' },
          yaxis: { title: 'Orders' },
          height: 350,
          paper_bgcolor: 'white',
          plot_bgcolor: 'white',
        }}
        config={{ responsive: true }}
        style={{ width: '100%' }}
      />
    </div>
  );

  const renderForecastBlock = (data, product) => (
    <div className="border rounded-lg p-4 bg-white w-full">
      <h3 className="text-xl font-semibold mb-4">{product} - Forecast</h3>
      <h4 className="mb-4">📦 Total Predicted Sales: <span className="text-green-600">{data?.total_forecast?.toFixed(2)}</span></h4>
      <Plot
        data={[
          {
            x: data?.forecast_data?.map((d) => d.ds),
            y: data?.forecast_data?.map((d) => d.yhat),
            type: 'scatter',
            mode: 'lines',
            name: 'Forecast',
            line: { color: 'blue' },
          },
          {
            x: data?.forecast_data?.map((d) => d.ds),
            y: data?.forecast_data?.map((d) => d.yhat_upper),
            type: 'scatter',
            mode: 'lines',
            name: 'Upper Bound',
            line: { dash: 'dash', color: 'lightblue' },
          },
          {
            x: data?.forecast_data?.map((d) => d.ds),
            y: data?.forecast_data?.map((d) => d.yhat_lower),
            type: 'scatter',
            mode: 'lines',
            name: 'Lower Bound',
            fill: 'tonexty',
            fillcolor: 'rgba(173,216,230,0.2)',
            line: { dash: 'dash', color: 'lightblue' },
          },
        ]}
        layout={{
          xaxis: { title: 'Date' },
          yaxis: { title: 'Predicted Sales' },
          height: 350,
          paper_bgcolor: 'white',
          plot_bgcolor: 'white',
        }}
        config={{ responsive: true }}
        style={{ width: '100%' }}
      />
    </div>
  );

  return (
    <div className="p-6 space-y-6 bg-background min-h-screen">
      <h1 className="text-3xl font-bold">🆚 Product Comparison Dashboard</h1>

      <div className="flex space-x-6">
        <div>
          <label className="block mb-2 font-medium">📡 Source System:</label>
          <select
            value={sourceSystem}
            onChange={(e) => setSourceSystem(e.target.value)}
            className="p-2 border rounded-md"
          >
            <option value="eon">EON</option>
            <option value="sdp">SDP</option>
            <option value="orion">ORION</option>
          </select>
        </div>
        <div>
          <label className="block mb-2 font-medium">📦 Product 1:</label>
          <Input value={product1} onChange={(e) => setProduct1(e.target.value)} placeholder="Enter Product 1" />
        </div>
        <div>
          <label className="block mb-2 font-medium">📦 Product 2:</label>
          <Input value={product2} onChange={(e) => setProduct2(e.target.value)} placeholder="Enter Product 2" />
        </div>
      </div>

      <Tabs defaultValue={timeRange} onValueChange={setTimeRange} className="w-full">
        <TabsList className="grid grid-cols-4 w-full">
          <TabsTrigger value="1w">1 Week</TabsTrigger>
          <TabsTrigger value="1m">1 Month</TabsTrigger>
          <TabsTrigger value="1y">1 Year</TabsTrigger>
          <TabsTrigger value="2y">2 Years</TabsTrigger>
        </TabsList>
        <TabsContent value={timeRange}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {product1 && trendData1 && renderTrendBlock(trendData1)}
            {product2 && trendData2 && renderTrendBlock(trendData2)}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            {product1 && forecastData1 && renderForecastBlock(forecastData1, product1)}
            {product2 && forecastData2 && renderForecastBlock(forecastData2, product2)}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ProductComparison;
