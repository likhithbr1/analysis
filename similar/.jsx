import React, { useEffect, useState, useRef } from "react";
import { Box, Typography, CircularProgress, Paper } from "@mui/material";
import axios from "axios";
import { AgGridReact } from "ag-grid-react";

import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "ag-grid-enterprise";

const ProductSimilarity = () => {
  const [rowData, setRowData] = useState([]);
  const [loading, setLoading] = useState(true);
  const gridRef = useRef();

  useEffect(() => {
    fetchSimilarityData();
  }, []);

  const fetchSimilarityData = async () => {
    try {
      const response = await axios.get("http://localhost:5000/similarity");
      const data = response.data.matches;

      const processed = data.map((row, index) => ({
        slNo: index + 1,
        ...row,
      }));

      setRowData(processed);
    } catch (err) {
      console.error("Failed to load product similarity data", err);
    } finally {
      setLoading(false);
    }
  };

  const columnDefs = [
    {
      headerName: "Sl No",
      field: "slNo",
      width: 80,
      sortable: false,
      filter: false,
      pinned: "left",
      cellStyle: { backgroundColor: "#f5f5f5", fontWeight: "bold" }
    },
    {
      headerName: "Orion Code",
      field: "Orion Code",
      filter: "agTextColumnFilter",
      sortable: true,
      resizable: true,
      cellStyle: { backgroundColor: "#d4edda" }
    },
    {
      headerName: "Orion Description",
      field: "Orion Description",
      filter: "agTextColumnFilter",
      sortable: true,
      resizable: true,
      flex: 1
    },
    {
      headerName: "SDP Code",
      field: "SDP Code",
      filter: "agTextColumnFilter",
      sortable: true,
      resizable: true,
      cellStyle: { backgroundColor: "#fff3cd" }
    },
    {
      headerName: "SDP Description",
      field: "SDP Description",
      filter: "agTextColumnFilter",
      sortable: true,
      resizable: true,
      flex: 1
    },
    {
      headerName: "Similarity Score",
      field: "Similarity Score",
      filter: "agNumberColumnFilter",
      sortable: true,
      resizable: true,
      type: "numericColumn"
    }
  ];

  const defaultColDef = {
    flex: 1,
    minWidth: 100,
    filter: true,
    sortable: true,
    resizable: true,
  };

  const onGridReady = (params) => {
    gridRef.current = params.api;
    params.api.sizeColumnsToFit(); // Auto-fit columns
  };

  return (
    <Box p={3}>
      <Typography variant="h4" mb={2}>🔍 Product Similarity Analysis</Typography>
      <Typography mb={3}>
        Compare products between Orion and SDP systems using semantic similarity. Threshold is fixed at 0.85.
      </Typography>

      {loading ? (
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper elevation={3}>
          <div
            className="ag-theme-alpine"
            style={{ height: 600, width: "100%" }}
          >
            <AgGridReact
              rowData={rowData}
              columnDefs={columnDefs}
              defaultColDef={defaultColDef}
              domLayout="autoHeight"
              animateRows={true}
              pagination={true}
              paginationPageSize={20}
              onGridReady={onGridReady}
            />
          </div>
        </Paper>
      )}
    </Box>
  );
};

export default ProductSimilarity;
