import React, { useEffect, useState } from "react";
import axios from "axios";
import Plot from "react-plotly.js";
import {
  Box,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Paper,
  Divider,
} from "@mui/material";

const DemandForecast = () => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState("");
  const [forecastData, setForecastData] = useState([]);
  const [totalForecast, setTotalForecast] = useState(null);
  const [loading, setLoading] = useState(false);

  const SOURCE_SYSTEM = "eon"; // hardcoded as per your request

  useEffect(() => {
    axios
      .post("http://localhost:5000/forecast/summary", { source_system: SOURCE_SYSTEM })
      .then((res) => {
        setProducts(res.data.products || []);
        // Automatically select the first product
        if (res.data.products.length > 0) {
          setSelectedProduct(res.data.products[0]);
        }
      })
      .catch((err) => console.error("Error fetching products:", err));
  }, []);

  useEffect(() => {
    if (!selectedProduct) return;
    setLoading(true);
    axios
      .post("http://localhost:5000/forecast/detail", {
        source_system: SOURCE_SYSTEM,
        product: selectedProduct,
      })
      .then((res) => {
        setForecastData(res.data.forecast_data || []);
        setTotalForecast(res.data.total_forecast || 0);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching forecast:", err);
        setLoading(false);
      });
  }, [selectedProduct]);

  const formatDate = (ds) => new Date(ds).toISOString().split("T")[0];

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        📈 30-Day Demand Forecast (Source: EON)
      </Typography>

      <FormControl fullWidth margin="normal">
        <InputLabel>Select Product</InputLabel>
        <Select
          value={selectedProduct}
          label="Select Product"
          onChange={(e) => setSelectedProduct(e.target.value)}
        >
          {products.map((product) => (
            <MenuItem key={product} value={product}>
              {product}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {loading && (
        <Box display="flex" justifyContent="center" my={3}>
          <CircularProgress />
        </Box>
      )}

      {!loading && forecastData.length > 0 && (
        <>
          <Box my={2}>
            <Typography variant="subtitle1">
              Total Forecast (30 Days): <strong>{totalForecast}</strong> units
            </Typography>
          </Box>

          <Divider sx={{ mb: 2 }} />

          <Plot
            data={[
              {
                x: forecastData.map((d) => formatDate(d.ds)),
                y: forecastData.map((d) => d.yhat),
                type: "scatter",
                mode: "lines",
                name: "Forecast",
                line: { color: "blue" },
              },
              {
                x: forecastData.map((d) => formatDate(d.ds)),
                y: forecastData.map((d) => d.yhat_upper),
                type: "scatter",
                mode: "lines",
                name: "Upper Bound",
                line: { dash: "dot", color: "lightblue" },
              },
              {
                x: forecastData.map((d) => formatDate(d.ds)),
                y: forecastData.map((d) => d.yhat_lower),
                type: "scatter",
                mode: "lines",
                name: "Lower Bound",
                fill: "tonexty",
                fillcolor: "rgba(173,216,230,0.2)",
                line: { dash: "dot", color: "lightblue" },
              },
            ]}
            layout={{
              title: `Forecast for ${selectedProduct}`,
              xaxis: { title: "Date" },
              yaxis: { title: "Predicted Daily Sales" },
              margin: { t: 50, l: 50, r: 30, b: 50 },
              hovermode: "x unified",
              autosize: true,
            }}
            useResizeHandler
            style={{ width: "100%", height: "400px" }}
          />
        </>
      )}
    </Paper>
  );
};

export default DemandForecast;
