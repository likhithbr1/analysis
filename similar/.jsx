import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  CircularProgress,
  Paper,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import axios from "axios";

const ProductSimilarity = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSimilarityData();
  }, []);

  const fetchSimilarityData = async () => {
    try {
      const response = await axios.get("http://localhost:5000/similarity");
      const data = response.data.matches;

      const processed = data.map((row, index) => ({
        id: index + 1, // required by DataGrid
        slNo: index + 1,
        ...row,
      }));

      setRows(processed);
    } catch (err) {
      console.error("Failed to load product similarity data", err);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      field: "slNo",
      headerName: "Sl No",
      width: 80,
      sortable: false,
      filterable: false,
    },
    { field: "Orion Code", headerName: "Orion Code", width: 150 },
    { field: "Orion Description", headerName: "Orion Description", width: 300, flex: 1 },
    { field: "SDP Code", headerName: "SDP Code", width: 150 },
    { field: "SDP Description", headerName: "SDP Description", width: 300, flex: 1 },
    { field: "Similarity Score", headerName: "Similarity", width: 130, type: "number" },
  ];

  return (
    <Box p={3}>
      <Typography variant="h4" mb={2}>🔍 Product Similarity Analysis</Typography>
      <Typography mb={3}>
        Compare products between Orion and SDP systems using semantic similarity. Threshold is fixed at 0.85.
      </Typography>

      {loading ? (
        <Box display="flex" justifyContent="center" mt={4}><CircularProgress /></Box>
      ) : (
        <Paper elevation={3}>
          <div style={{ height: 600, width: '100%' }}>
            <DataGrid
              rows={rows}
              columns={columns}
              disableRowSelectionOnClick
              pagination
              pageSize={20}
              rowsPerPageOptions={[20, 50, 100]}
              filterModel={{
                items: [],
              }}
              sortingOrder={['desc', 'asc']}
            />
          </div>
        </Paper>
      )}
    </Box>
  );
};

export default ProductSimilarity;
