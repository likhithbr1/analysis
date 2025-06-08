import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import axios from "axios";
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
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Collapse,
} from "@mui/material";

const DemandForecast = () => {
  const [forecastData, setForecastData] = useState([]);
  const [productList, setProductList] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState("");
  const [totalForecast, setTotalForecast] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showTable, setShowTable] = useState(false);

  const fetchData = async () => {
    try {
      const res = await axios.get("http://localhost:5000/forecast/data");
      const rawData = res.data.forecast_data || [];
      const product = res.data.product || "";
      const total = res.data.total_forecast || 0;

      setForecastData(rawData);
      setSelectedProduct(product);
      setTotalForecast(total);

      // Extract product list from forecast data
      const uniqueProducts = [
        ...new Set(rawData.map((item) => item.product_name)),
      ];
      setProductList(uniqueProducts);
    } catch (error) {
      console.error("Error fetching forecast data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredData = forecastData.filter(
    (item) => item.product_name === selectedProduct
  );

  const chartData = [
    {
      x: filteredData.map((d) => new Date(d.ds).toISOString()),
      y: filteredData.map((d) => d.yhat),
      type: "scatter",
      mode: "lines",
      name: "Forecast (yhat)",
      line: { color: "blue" },
    },
    {
      x: filteredData.map((d) => new Date(d.ds).toISOString()),
      y: filteredData.map((d) => d.yhat_upper),
      type: "scatter",
      mode: "lines",
      name: "Upper Bound",
      line: { dash: "dash", color: "lightblue" },
    },
    {
      x: filteredData.map((d) => new Date(d.ds).toISOString()),
      y: filteredData.map((d) => d.yhat_lower),
      type: "scatter",
      mode: "lines",
      name: "Lower Bound",
      line: { dash: "dash", color: "lightblue" },
      fill: "tonexty",
      fillcolor: "rgba(173,216,230,0.2)",
    },
  ];

  if (loading) {
    return (
      <Box textAlign="center" mt={10}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        📈 30-Day Sales Forecast
      </Typography>

      <FormControl fullWidth sx={{ maxWidth: 400, mb: 3 }}>
        <InputLabel>Select Product</InputLabel>
        <Select
          value={selectedProduct}
          label="Select Product"
          onChange={(e) => setSelectedProduct(e.target.value)}
        >
          {productList.map((prod) => (
            <MenuItem key={prod} value={prod}>
              {prod}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Typography variant="h6" sx={{ mb: 2 }}>
        📦 Total Predicted Sales for Next 30 Days:{" "}
        <strong>{totalForecast.toFixed(2)}</strong> units
      </Typography>

      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <Plot
          data={chartData}
          layout={{
            title: `30-Day Forecast for '${selectedProduct}'`,
            xaxis: { title: "Date" },
            yaxis: { title: "Predicted Daily Sales" },
            hovermode: "x unified",
          }}
          useResizeHandler
          style={{ width: "100%", height: "100%" }}
        />
      </Paper>

      <Typography
        variant="subtitle1"
        sx={{ cursor: "pointer", color: "blue", mb: 1 }}
        onClick={() => setShowTable(!showTable)}
      >
        📄 {showTable ? "Hide Forecast Table" : "Show Forecast Table"}
      </Typography>

      <Collapse in={showTable}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Forecast (yhat)</TableCell>
              <TableCell>Lower Bound</TableCell>
              <TableCell>Upper Bound</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredData.map((row, idx) => (
              <TableRow key={idx}>
                <TableCell>{new Date(row.ds).toLocaleDateString()}</TableCell>
                <TableCell>{row.yhat.toFixed(2)}</TableCell>
                <TableCell>{row.yhat_lower.toFixed(2)}</TableCell>
                <TableCell>{row.yhat_upper.toFixed(2)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Collapse>
    </Box>
  );
};

export default DemandForecast;
