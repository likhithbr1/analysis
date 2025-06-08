// ProductBundling.jsx
import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Grid,
  Paper,
  Tabs,
  Tab,
  Button,
  Divider,
  CircularProgress,
} from "@mui/material";
import axios from "axios";

const ProductBundling = () => {
  const [tab, setTab] = useState(0);
  const [bundles, setBundles] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const sourceSystem = "eon";

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [bundleRes, recRes] = await Promise.all([
        axios.post("http://localhost:5000/bundles", { source_system: sourceSystem }),
        axios.post("http://localhost:5000/recommendations", { source_system: sourceSystem }),
      ]);
      setBundles(bundleRes.data.bundles || []);
      setRecommendations(recRes.data.recommendations || []);
    } catch (err) {
      console.error("Error fetching data", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h4" mb={2}>Smart Product Suggestions</Typography>
      <Tabs value={tab} onChange={(_, val) => setTab(val)} sx={{ mb: 2 }}>
        <Tab label="📦 Product Bundles" />
        <Tab label="🎯 Smart Recommendations" />
      </Tabs>

      {loading ? (
        <Box display="flex" justifyContent="center" mt={5}><CircularProgress /></Box>
      ) : (
        <>
          {tab === 0 && (
            <Grid container spacing={3}>
              {bundles.slice(0, 12).map((bundle, i) => (
                <Grid item xs={12} sm={6} md={4} key={i}>
                  <Paper elevation={4} sx={{
                    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    color: "white",
                    borderRadius: "15px",
                    padding: "20px",
                    textAlign: "center"
                  }}>
                    <Typography variant="h6">{bundle.length}-Item Bundle</Typography>
                    <Box my={2}>
                      {bundle.itemsets.map((item, idx) => (
                        <Typography key={idx}>• {item}</Typography>
                      ))}
                    </Box>
                    <Typography variant="h5">📈 {bundle.support_count} orders</Typography>
                    <Typography>({(bundle.support * 100).toFixed(1)}% of all orders)</Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          )}

          {tab === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                🔮 Smart Recommendations
              </Typography>
              <Typography mb={2} fontStyle="italic">
                When customers buy certain products together, they often purchase additional items. Here are the patterns we've discovered:
              </Typography>

              {recommendations.length === 0 ? (
                <Typography>No recommendation patterns found with 60% confidence threshold.</Typography>
              ) : (
                recommendations.map((rec, idx) => (
                  <Paper
                    key={idx}
                    sx={{
                      borderLeft: "4px solid #667eea",
                      background: "#f8f9fa",
                      borderRadius: "10px",
                      padding: "20px",
                      mb: 3,
                    }}
                  >
                    <Typography variant="h6" mb={1}>Recommendation Pattern #{idx + 1}</Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography fontWeight="bold">If customers buy:</Typography>
                        {rec.antecedents.map((item, i) => (
                          <Button key={i} disabled fullWidth variant="outlined" sx={{ my: 0.5 }}>
                            📦 {item}
                          </Button>
                        ))}
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography fontWeight="bold">They often also buy:</Typography>
                        {rec.consequents.map((item, i) => (
                          <Button key={i} fullWidth variant="contained" sx={{ my: 0.5 }}>
                            💡 {item}
                          </Button>
                        ))}
                      </Grid>
                    </Grid>
                    <Typography mt={2}>
                      <strong>Confidence:</strong> {(rec.confidence * 100).toFixed(2)}%
                    </Typography>
                  </Paper>
                ))
              )}
            </Box>
          )}

          <Divider sx={{ my: 4 }} />
          <Typography align="center" color="text.secondary">
            🤖 Powered by FP-Growth Algorithm & Association Rules Mining <br />
            💡 Showing recommendations with 60% confidence or higher
          </Typography>
        </>
      )}
    </Box>
  );
};

export default ProductBundling;
