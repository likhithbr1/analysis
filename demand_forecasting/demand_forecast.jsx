import React, { useState, useEffect } from "react";
import axios from "axios";
import Plot from "react-plotly.js";

const DemandForecast = () => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState("");
  const [forecastData, setForecastData] = useState(null);
  const [tableVisible, setTableVisible] = useState(false);
  const [loading, setLoading] = useState(false);

  const SOURCE = "eon"; // or "abc", "xyz" depending on dropdown if needed

  useEffect(() => {
    axios
      .post("http://localhost:5000/forecast/summary", {
        source_system: SOURCE,
        analysis_type: "forecast"
      })
      .then((res) => {
        setProducts(res.data.products);
        setSelectedProduct(res.data.products[0]);
      });
  }, []);

  useEffect(() => {
    if (selectedProduct) {
      setLoading(true);
      axios
        .post("http://localhost:5000/forecast/detail", {
          source_system: SOURCE,
          analysis_type: "forecast",
          product: selectedProduct
        })
        .then((res) => {
          setForecastData(res.data);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }
  }, [selectedProduct]);

  return (
    <div className="forecast-container">
      <h2>📈 30-Day Sales Forecast</h2>

      <select
        value={selectedProduct}
        onChange={(e) => setSelectedProduct(e.target.value)}
      >
        {products.map((prod) => (
          <option key={prod} value={prod}>
            {prod}
          </option>
        ))}
      </select>

      {loading && <p>Loading forecast...</p>}

      {forecastData && (
        <>
          <h3>📦 Predicted Sales: {forecastData.total_forecast.toFixed(2)} units</h3>

          <Plot
            data={[
              {
                x: forecastData.dates,
                y: forecastData.yhat,
                type: "scatter",
                mode: "lines",
                name: "Forecast (yhat)",
                line: { color: "blue" }
              },
              {
                x: forecastData.dates,
                y: forecastData.yhat_upper,
                type: "scatter",
                mode: "lines",
                name: "Upper Bound",
                line: { color: "lightblue", dash: "dash" }
              },
              {
                x: forecastData.dates,
                y: forecastData.yhat_lower,
                type: "scatter",
                mode: "lines",
                name: "Lower Bound",
                line: { color: "lightblue", dash: "dash" },
                fill: "tonexty",
                fillcolor: "rgba(173,216,230,0.2)"
              }
            ]}
            layout={{
              title: `30-Day Forecast for '${selectedProduct}'`,
              xaxis: { title: "Date" },
              yaxis: { title: "Predicted Daily Sales" },
              hovermode: "x unified"
            }}
            useResizeHandler
            style={{ width: "100%", height: "100%" }}
          />

          <button onClick={() => setTableVisible(!tableVisible)}>
            {tableVisible ? "Hide Table" : "📄 Show Forecast Table"}
          </button>

          {tableVisible && (
            <table className="forecast-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>yhat</th>
                  <th>yhat_lower</th>
                  <th>yhat_upper</th>
                </tr>
              </thead>
              <tbody>
                {forecastData.dates.map((date, i) => (
                  <tr key={i}>
                    <td>{date}</td>
                    <td>{forecastData.yhat[i].toFixed(2)}</td>
                    <td>{forecastData.yhat_lower[i].toFixed(2)}</td>
                    <td>{forecastData.yhat_upper[i].toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </div>
  );
};

export default DemandForecast;
