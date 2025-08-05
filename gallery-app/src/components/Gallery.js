import React, { useState, useEffect } from 'react';
import GLightbox from 'glightbox';
import 'glightbox/dist/css/glightbox.min.css';

const Gallery = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter states
  const [showNames, setShowNames] = useState(true);
  const [showDates, setShowDates] = useState(true);
  const [showLinks, setShowLinks] = useState(false);
  const [hideDuplicates, setHideDuplicates] = useState(false);
  const [fileTypes, setFileTypes] = useState({});
  const [enabledFileTypes, setEnabledFileTypes] = useState({});

  // Initialize lightbox
  useEffect(() => {
    GLightbox({
      selector: '.glightbox',
      touchNavigation: true,
      loop: true,
      openEffect: 'zoom',
      closeEffect: 'zoom',
      zoomable: true
    });
  }, [files]);

  // Load data from report.json and analyze file types
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('./report.json');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setFiles(data);

        // Analyze file extensions
        const types = {};
        data.forEach(file => {
          const ext = file.file.split('.').pop().toLowerCase();
          types[ext] = (types[ext] || 0) + 1;
        });

        setFileTypes(types);

        // Enable all file types by default
        const enabled = {};
        Object.keys(types).forEach(ext => {
          enabled[ext] = true;
        });
        setEnabledFileTypes(enabled);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Helper functions
  const getFileName = (path) => path.split('\\').pop().split('/').pop();
  const getFileNameWithoutExt = (path) => getFileName(path).split('.').slice(0, -1).join('.');
  const isImage = (file) => /\.(jpe?g|png|gif|bmp|webp)$/i.test(file);
  const formatDate = (dateString) => new Date(dateString).toLocaleString();

  // Toggle file type
  const toggleFileType = (ext) => {
    setEnabledFileTypes(prev => ({
      ...prev,
      [ext]: !prev[ext]
    }));
  };

  // Filter and process files
  const getFilteredFiles = () => {
    let filtered = [...files];

    // Filter by enabled file types
    filtered = filtered.filter(file => {
      const ext = file.file.split('.').pop().toLowerCase();
      return enabledFileTypes[ext];
    });

    if (hideDuplicates) {
      const seenNames = new Set();
      filtered = filtered.filter(file => {
        const nameWithoutExt = getFileNameWithoutExt(file.file);
        if (seenNames.has(nameWithoutExt)) {
          return false;
        }
        seenNames.add(nameWithoutExt);
        return true;
      });
    }

    return filtered;
  };

  const filteredFiles = getFilteredFiles();

  if (loading) {
    return (
      <div className="loading">
        <p>Loading gallery data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        <p>Error loading gallery data: {error}</p>
        <p>Please make sure report.json exists in the root directory.</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="gallery-container">
        <h1>Media Gallery</h1>

        {filteredFiles.length === 0 ? (
          <div className="no-files">
            <p>No files match the current filters</p>
          </div>
        ) : (
          <div className="gallery">
            {filteredFiles.map((item, index) => {
              const fileName = getFileName(item.file);
              const fileNameWithoutExt = getFileNameWithoutExt(item.file);

              return (
                <div key={`${item.hash}-${index}`} className="gallery-item">
                  {isImage(item.file) ? (
                    <a
                      href={item.link}
                      className="glightbox"
                      data-glightbox={`title: ${showNames ? fileName : ''}; description: ${
                        showDates ? `Uploaded: ${formatDate(item.date)}` : ''
                      } ${showLinks ? `Link: ${item.link}` : ''}`}
                    >
                      <img src={item.link} alt={fileName} loading="lazy" />
                      <div className="caption">
                        {showNames && <h3>{fileName}</h3>}
                        {showDates && <p>{formatDate(item.date)}</p>}
                        {showLinks && (
                          <p className="file-link">
                            <div className="file-link-text">
                              {item.link}
                            </div>
                          </p>
                        )}
                      </div>
                    </a>
                  ) : (
                    <a href={item.link} target="_blank" rel="noopener noreferrer">
                      <div className="file-icon">📄</div>
                      <div className="caption">
                        {showNames && <h3>{fileName}</h3>}
                        {showDates && <p>{formatDate(item.date)}</p>}
                        {showLinks && (
                          <p className="file-link">
                            <div className="file-link-text">
                              {item.link}
                            </div>
                          </p>
                        )}
                      </div>
                    </a>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="controls-panel">
        <h2>Display Options</h2>
        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={showNames}
              onChange={() => setShowNames(!showNames)}
            />
            Show file names
          </label>
        </div>
        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={showDates}
              onChange={() => setShowDates(!showDates)}
            />
            Show dates
          </label>
        </div>
        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={showLinks}
              onChange={() => setShowLinks(!showLinks)}
            />
            Show links
          </label>
        </div>
        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={hideDuplicates}
              onChange={() => setHideDuplicates(!hideDuplicates)}
            />
            Hide duplicate names (without extension)
          </label>
        </div>

        <h3>File Types</h3>
        {Object.keys(fileTypes).map(ext => (
          <div className="control-group" key={ext}>
            <label>
              <input
                type="checkbox"
                checked={enabledFileTypes[ext] || false}
                onChange={() => toggleFileType(ext)}
              />
              {`.${ext} (${fileTypes[ext]})`}
            </label>
          </div>
        ))}

        <div className="stats">
          <p>Showing: {filteredFiles.length} of {files.length} files</p>
          {hideDuplicates && (
            <p className="duplicates-note">
              (Hiding {files.length - filteredFiles.length} files with duplicate names)
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Gallery;