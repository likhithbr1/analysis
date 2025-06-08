// TrendAnalysis.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';

const TrendAnalysis = () => {
  const [summaryData, setSummaryData] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [timeRange, setTimeRange] = useState('1m');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      const response = await axios.post('http://localhost:5000/analysis/summary', {
        source_system: 'eon',
        analysis_type: 'trend_analysis'
      });
      setSummaryData(response.data);
    } catch (error) {
      console.error('Error fetching summary:', error);
    }
  };

  const fetchDetail = async (product, range) => {
    try {
      const response = await axios.post('http://localhost:5000/analysis/detail', {
        source_system: 'eon',
        analysis_type: 'trend_analysis',
        product,
        time_range: range
      });
      setDetailData(response.data);
    } catch (error) {
      console.error('Error fetching detail:', error);
    }
  };

  const handleProductClick = (product) => {
    setSelectedProduct(product);
    fetchDetail(product, timeRange);
  };

  const renderSparkline = (data, color) => (
    <Plot
      data={[{
        x: data.map(d => d.date),
        y: data.map(d => d.total_orders),
        type: 'scatter',
        mode: 'lines',
        line: { color, width: 2 },
        hoverinfo: 'skip'
      }]}
      layout={{ margin: { l: 0, r: 0, t: 0, b: 0 }, xaxis: { visible: false }, yaxis: { visible: false }, height: 40 }}
      config={{ displayModeBar: false }}
    />
  );

  const renderGrid = () => (
    <>
      <h2>All Product Trends</h2>
      <input
        type="text"
        placeholder="🔍 Search Product"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        {summaryData
          .filter(item => item.product.toLowerCase().includes(search.toLowerCase()))
          .map((item, index) => (
            <div key={index} style={{ border: '1px solid #ccc', borderRadius: 8, padding: 10, margin: 10, width: '30%' }}>
              <button onClick={() => handleProductClick(item.product)}><b>{item.product}</b></button>
              <p><strong>📦 Total Sales:</strong> {item.total_sales}</p>
              <p><strong>{item.trend_icon} {item.trend_description} ({item.trend_percent}%)</strong></p>
              {renderSparkline(item.sparkline_data, item.color)}
            </div>
        ))}
      </div>
    </>
  );

  const renderDetail = () => (
    <>
      <h2>📊 Detailed View: {detailData.product}</h2>
      <button onClick={() => { setSelectedProduct(null); setDetailData(null); }}>🔙 Back to All Products</button>
      <div style={{ marginTop: 10 }}>
        <label>Time Range: </label>
        <select value={timeRange} onChange={(e) => { setTimeRange(e.target.value); fetchDetail(selectedProduct, e.target.value); }}>
          <option value="1w">1 Week</option>
          <option value="1m">1 Month</option>
          <option value="1y">1 Year</option>
          <option value="2y">2 Years</option>
        </select>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 20 }}>
        <div><h4>Total Sales</h4><p>{detailData.total_sales}</p></div>
        <div><h4>Average Daily Sales</h4><p>{detailData.avg_sales}</p></div>
        <div><h4>Trend</h4><p>{detailData.trend_description} ({detailData.trend_percent}%)</p></div>
      </div>
      <Plot
        data={[
          {
            x: detailData.chart_data.dates,
            y: detailData.chart_data.actual,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Daily Orders',
            line: { color: 'royalblue', width: 2 },
            marker: { size: 6 }
          },
          {
            x: detailData.chart_data.dates,
            y: detailData.chart_data.trendline,
            type: 'scatter',
            mode: 'lines',
            name: 'Trend Line',
            line: { color: detailData.trend_percent < 0 ? 'red' : 'green', dash: 'dash', width: 2 }
          }
        ]}
        layout={{
          title: `${detailData.product.toUpperCase()} - ${timeRange.toUpperCase()} Analysis`,
          xaxis: { title: 'Date' },
          yaxis: { title: 'Orders' },
          height: 500,
          legend: { orientation: 'h' }
        }}
      />
    </>
  );

  return (
    <div style={{ padding: 20 }}>
      <h1>📈 Product Sales Trend Dashboard</h1>
      {!selectedProduct ? renderGrid() : (detailData ? renderDetail() : <p>Loading...</p>)}
    </div>
  );
};

export default TrendAnalysis;
