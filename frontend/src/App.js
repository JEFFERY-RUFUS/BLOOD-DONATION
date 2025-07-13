import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [plants, setPlants] = useState([]);
  const [selectedPlant, setSelectedPlant] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({});

  // Load initial data
  useEffect(() => {
    loadPlants();
    loadAlerts();
    loadDashboardStats();
  }, []);

  const loadPlants = async () => {
    try {
      const response = await axios.get(`${API}/plants`);
      setPlants(response.data);
      if (response.data.length > 0 && !selectedPlant) {
        setSelectedPlant(response.data[0]);
      }
    } catch (error) {
      console.error('Error loading plants:', error);
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await axios.get(`${API}/alerts`);
      setAlerts(response.data.filter(alert => !alert.resolved));
    } catch (error) {
      console.error('Error loading alerts:', error);
    }
  };

  const loadDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
    }
  };

  const DashboardView = () => (
    <div className="dashboard-grid">
      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-icon">🌱</div>
          <div className="stat-content">
            <h3>{dashboardStats.total_plants || 0}</h3>
            <p>Total Plants</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🔬</div>
          <div className="stat-content">
            <h3>{dashboardStats.total_detections || 0}</h3>
            <p>Health Scans</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <h3>{dashboardStats.active_alerts || 0}</h3>
            <p>Active Alerts</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">💚</div>
          <div className="stat-content">
            <h3>{dashboardStats.health_percentage || 0}%</h3>
            <p>Health Rate</p>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="section">
          <h2>🚨 Recent Alerts</h2>
          <div className="alerts-list">
            {alerts.length === 0 ? (
              <p className="no-alerts">No active alerts - All plants are healthy! 🌿</p>
            ) : (
              alerts.slice(0, 5).map(alert => (
                <div key={alert.id} className={`alert-item ${alert.severity}`}>
                  <div className="alert-content">
                    <strong>{alert.message}</strong>
                    <span className="alert-time">
                      {new Date(alert.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <button 
                    onClick={() => resolveAlert(alert.id)}
                    className="resolve-btn"
                  >
                    ✓
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="section">
          <h2>🌱 My Plants</h2>
          <div className="plants-grid">
            {plants.map(plant => (
              <div key={plant.id} className="plant-card" onClick={() => setSelectedPlant(plant)}>
                <div className="plant-image">
                  <img src="https://images.unsplash.com/photo-1653842648072-a1beef80c4aa?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwxfHxwbGFudCUyMGNhcmV8ZW58MHx8fGdyZWVufDE3NTI0MjY2NTN8MA&ixlib=rb-4.1.0&q=85" alt={plant.name} />
                </div>
                <div className="plant-info">
                  <h3>{plant.name}</h3>
                  <p>{plant.plant_type}</p>
                  <span className={`status ${plant.health_status}`}>
                    {plant.health_status}
                  </span>
                </div>
              </div>
            ))}
            <div className="plant-card add-plant" onClick={() => setActiveTab('add-plant')}>
              <div className="add-icon">+</div>
              <p>Add New Plant</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const DiseaseDetectionView = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [detectionResult, setDetectionResult] = useState(null);
    const [detectingDisease, setDetectingDisease] = useState(false);

    const handleFileSelect = (event) => {
      const file = event.target.files[0];
      if (file) {
        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(file));
        setDetectionResult(null);
      }
    };

    const detectDisease = async () => {
      if (!selectedFile || !selectedPlant) return;

      setDetectingDisease(true);
      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        const response = await axios.post(`${API}/detect-disease/${selectedPlant.id}`, formData);
        setDetectionResult(response.data);
        loadAlerts(); // Refresh alerts
      } catch (error) {
        console.error('Error detecting disease:', error);
        alert('Error analyzing image. Please try again.');
      } finally {
        setDetectingDisease(false);
      }
    };

    return (
      <div className="disease-detection">
        <div className="detection-header">
          <h2>🔬 AI Disease Detection</h2>
          <p>Upload a photo of your plant's leaves for instant disease analysis</p>
        </div>

        <div className="detection-content">
          <div className="upload-section">
            <div className="file-upload">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="file-input"
                id="plant-image"
              />
              <label htmlFor="plant-image" className="file-label">
                {previewUrl ? (
                  <img src={previewUrl} alt="Plant preview" className="preview-image" />
                ) : (
                  <div className="upload-placeholder">
                    <div className="upload-icon">📸</div>
                    <p>Click to upload plant image</p>
                  </div>
                )}
              </label>
            </div>

            <div className="plant-selector">
              <label>Select Plant:</label>
              <select 
                value={selectedPlant?.id || ''} 
                onChange={(e) => setSelectedPlant(plants.find(p => p.id === e.target.value))}
              >
                {plants.map(plant => (
                  <option key={plant.id} value={plant.id}>
                    {plant.name} ({plant.plant_type})
                  </option>
                ))}
              </select>
            </div>

            <button 
              onClick={detectDisease}
              disabled={!selectedFile || !selectedPlant || detectingDisease}
              className="analyze-btn"
            >
              {detectingDisease ? 'Analyzing...' : 'Analyze Plant Health'}
            </button>
          </div>

          {detectionResult && (
            <div className="detection-results">
              <h3>Analysis Results</h3>
              <div className={`result-card ${detectionResult.severity.toLowerCase()}`}>
                <div className="result-header">
                  <h4>{detectionResult.disease_name}</h4>
                  <span className="confidence">
                    {detectionResult.confidence}% confidence
                  </span>
                </div>
                
                <div className="result-details">
                  <p><strong>Severity:</strong> {detectionResult.severity}</p>
                  <p><strong>Description:</strong> {detectionResult.description}</p>
                  
                  <div className="treatment-section">
                    <strong>Treatment:</strong>
                    <p>{detectionResult.treatment}</p>
                  </div>

                  <div className="recommendations">
                    <strong>Recommendations:</strong>
                    <ul>
                      {detectionResult.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const AddPlantView = () => {
    const [newPlant, setNewPlant] = useState({ name: '', plant_type: '' });

    const addPlant = async () => {
      if (!newPlant.name || !newPlant.plant_type) return;

      try {
        await axios.post(`${API}/plants`, newPlant);
        setNewPlant({ name: '', plant_type: '' });
        loadPlants();
        setActiveTab('dashboard');
      } catch (error) {
        console.error('Error adding plant:', error);
      }
    };

    return (
      <div className="add-plant-form">
        <h2>🌱 Add New Plant</h2>
        <div className="form-group">
          <label>Plant Name:</label>
          <input
            type="text"
            value={newPlant.name}
            onChange={(e) => setNewPlant({ ...newPlant, name: e.target.value })}
            placeholder="e.g., My Tomato Plant"
          />
        </div>
        <div className="form-group">
          <label>Plant Type:</label>
          <select
            value={newPlant.plant_type}
            onChange={(e) => setNewPlant({ ...newPlant, plant_type: e.target.value })}
          >
            <option value="">Select plant type</option>
            <option value="Tomato">Tomato</option>
            <option value="Pepper">Pepper</option>
            <option value="Lettuce">Lettuce</option>
            <option value="Basil">Basil</option>
            <option value="Rose">Rose</option>
            <option value="Orchid">Orchid</option>
            <option value="Succulent">Succulent</option>
            <option value="Fern">Fern</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <button onClick={addPlant} className="add-plant-btn">
          Add Plant
        </button>
      </div>
    );
  };

  const resolveAlert = async (alertId) => {
    try {
      await axios.patch(`${API}/alerts/${alertId}/resolve`);
      loadAlerts();
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🌿 AI Plant Care System</h1>
          <p>Smart plant monitoring with AI-powered disease detection</p>
        </div>
      </header>

      <nav className="app-nav">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={activeTab === 'disease-detection' ? 'active' : ''}
          onClick={() => setActiveTab('disease-detection')}
        >
          Disease Detection
        </button>
        <button 
          className={activeTab === 'add-plant' ? 'active' : ''}
          onClick={() => setActiveTab('add-plant')}
        >
          Add Plant
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'dashboard' && <DashboardView />}
        {activeTab === 'disease-detection' && <DiseaseDetectionView />}
        {activeTab === 'add-plant' && <AddPlantView />}
      </main>

      <footer className="app-footer">
        <p>AI-Powered Smart Plant Care System | Keeping your plants healthy 🌱</p>
      </footer>
    </div>
  );
};

export default App;