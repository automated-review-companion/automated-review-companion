import { Tooltip } from '@mui/material';
import Papa from 'papaparse';
import React, { useState } from 'react';
import { toast } from 'react-toastify';

export interface CsvImportFieldProps {
  tooltip: string
}

const CsvImportField: React.FC<CsvImportFieldProps> = (props) => {
  const { tooltip } = props;
  const [dragActive, setDragActive] = useState(false);
  
  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "text/csv") {
        parseCsv(file);
      } else {
        toast.error("Invalid file type. Please upload a CSV file.");
      }
    }
  };

  const parseCsv = (file: File) => {
    const dois = [];
    Papa.parse(file, {
      complete: function(results: any) {
        const data = results.data;
        if (data.length > 0) {
          // Find the DOI column index (assuming header in first row)
          const header = data[0];
          const doiIndex = header.indexOf('DOI');

          if (doiIndex === -1) {
            console.error("No 'DOI' column found in the CSV file.");
            return;
          }

          // Iterate over each row, skipping the header
          for (let i = 1; i < data.length; i++) {
            const row = data[i];
            const doi = row[doiIndex];
            if (doi) {
              dois.push(doi);
            }
          }
        }
      },
      header: true // CSV containing headers
    });
  };


  return (
    <Tooltip title={tooltip} placement="right" style={{ cursor: "pointer" }}>
      <div
        className={`input-group-prepend ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={(e) => handleDrag(e)}
        onDragLeave={(e) => handleDrag(e)}
        onDragOver={(e) => handleDrag(e)}
        onDrop={(e) => handleDrop(e)}
      >
        <span className="input-group-text rounded-0" id="basic-addon1">
          Import CSV
        </span>
        {dragActive && <div className="drag-overlay">Drop your file here</div>}
      </div>
    </Tooltip>
  );
};

export default CsvImportField;
