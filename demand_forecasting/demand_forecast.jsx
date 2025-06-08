import React, { useEffect, useState } from "react";
import axios from "axios";
import Plot from "react-plotly.js";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
} from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronRight } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const DemandForecast = () => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState("");
  const [forecastData, setForecastData] = useState([]);
  const [totalForecast, setTotalForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isTableOpen, setIsTableOpen] = useState(false);

  const SOURCE_SYSTEM = "eon";

  useEffect(() => {
    axios
      .post("http://localhost:5000/forecast/summary", { source_system: SOURCE_SYSTEM })
      .then((res) => {
        const sortedProducts = (res.data.products || []).sort();
        setProducts(sortedProducts);
        if (sortedProducts.length > 0) {
          setSelectedProduct(sortedProducts[0]);
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
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">📈 30-Day Sales Forecast</h1>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">
            🔍 Select a product to view forecast
          </label>
          <Select value={selectedProduct} onValueChange={setSelectedProduct}>
            <SelectTrigger className="w-full max-w-md">
              <SelectValue placeholder="Select a product" />
            </SelectTrigger>
            <SelectContent>
              {products.map((product) => (
                <SelectItem key={product} value={product}>
                  {product}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {loading && (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        )}

        {!loading && forecastData.length > 0 && (
          <>
            <div className="mb-6">
              <h3 className="text-xl font-semibold">
                📦 Total Predicted Sales for Next 30 Days:{" "}
                <code className="bg-muted px-2 py-1 rounded text-sm text-green-600">
                  {totalForecast?.toFixed(2)}
                </code>{" "}
                units
              </h3>
            </div>

            <div className="mb-6 w-full">
              <Plot
                data={[
                  {
                    x: forecastData.map((d) => formatDate(d.ds)),
                    y: forecastData.map((d) => d.yhat),
                    type: "scatter",
                    mode: "lines",
                    name: "Forecast (yhat)",
                    line: { color: "blue" },
                  },
                  {
                    x: forecastData.map((d) => formatDate(d.ds)),
                    y: forecastData.map((d) => d.yhat_upper),
                    type: "scatter",
                    mode: "lines",
                    name: "Upper Bound",
                    line: { dash: "dash", color: "lightblue" },
                  },
                  {
                    x: forecastData.map((d) => formatDate(d.ds)),
                    y: forecastData.map((d) => d.yhat_lower),
                    type: "scatter",
                    mode: "lines",
                    name: "Lower Bound",
                    fill: "tonexty",
                    fillcolor: "rgba(173,216,230,0.2)",
                    line: { dash: "dash", color: "lightblue" },
                  },
                ]}
                layout={{
                  title: {
                    text: `30-Day Forecast for '${selectedProduct}'`,
                    font: { size: 18 },
                    pad: { t: 20, b: 10 },
                  },
                  xaxis: { title: "Date" },
                  yaxis: { title: "Predicted Daily Sales" },
                  legend: {
                    orientation: "h",
                    x: 0,
                    y: 1.15,
                  },
                  margin: { t: 80, l: 60, r: 40, b: 60 },
                  hovermode: "x unified",
                  autosize: true,
                  font: { size: 12 },
                }}
                useResizeHandler
                style={{ width: "100%" }}
                config={{ responsive: true, displayModeBar: true }}
              />
            </div>

            <Collapsible open={isTableOpen} onOpenChange={setIsTableOpen}>
              <CollapsibleTrigger asChild>
                <Button variant="outline" className="w-full justify-between mb-4">
                  <span>📄 Show Forecast Table</span>
                  {isTableOpen ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="transition-all duration-300">
                <Card>
                  <CardContent className="p-0">
                    <div className="max-h-96 overflow-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Date</TableHead>
                            <TableHead>Forecast (yhat)</TableHead>
                            <TableHead>Lower Bound</TableHead>
                            <TableHead>Upper Bound</TableHead>
                            <TableHead>Product</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {forecastData.map((row, index) => (
                            <TableRow key={index}>
                              <TableCell>{formatDate(row.ds)}</TableCell>
                              <TableCell>{row.yhat?.toFixed(4)}</TableCell>
                              <TableCell>{row.yhat_lower?.toFixed(4)}</TableCell>
                              <TableCell>{row.yhat_upper?.toFixed(4)}</TableCell>
                              <TableCell>{selectedProduct}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>
              </CollapsibleContent>
            </Collapsible>
          </>
        )}
      </div>
    </div>
  );
};

export default DemandForecast;
