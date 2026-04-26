import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import LoadingSpinner from '../components/LoadingSpinner';

const FlightSearchPage = () => {
  const [airports, setAirports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');
  const [date, setDate] = useState('');
  const [seatClass, setSeatClass] = useState('economy');

  const navigate = useNavigate();

  useEffect(() => {
    const fetchAirports = async () => {
      try {
        const response = await api.get('/flights/');
        const flights = response.data.data.items || response.data.data || [];
        
        // Extract unique source airports
        const uniqueAirportsMap = new Map();
        flights.forEach(f => {
          if (f.source && f.source.iata) {
            uniqueAirportsMap.set(f.source.iata, f.source);
          } else if (f.source_iata) { // Fallback based on typical schematics
             uniqueAirportsMap.set(f.source_iata, { iata: f.source_iata, city: 'Unknown' });
          }
        });
        
        // If the endpoint returned string IATAs instead of objects, let's gracefully handle
        if (uniqueAirportsMap.size === 0 && flights.length > 0) {
           flights.forEach(f => {
             if (typeof f.source === 'string') {
               uniqueAirportsMap.set(f.source, { iata: f.source, city: '' });
             }
           });
        }
        
        setAirports(Array.from(uniqueAirportsMap.values()));
      } catch (err) {
        setError('Failed to load routes. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    fetchAirports();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (!source || !destination || !date) return;
    
    navigate(`/flights/results?source=${source}&destination=${destination}&date=${date}&class=${seatClass}`);
  };

  const handleQuickSearch = (src, dest) => {
    setSource(src);
    setDestination(dest);
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setDate(tomorrow.toISOString().split('T')[0]);
    // It will not auto submit, just pre-fill
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="animate-fade-in" style={{ padding: '3rem 1rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div className="text-center mb-10">
        <h1 style={{ fontSize: '3rem', fontWeight: 800, color: 'white', marginBottom: '1rem' }}>Find Your Perfect Flight</h1>
        <p style={{ color: '#94a3b8', fontSize: '1.125rem' }}>Search from hundreds of destinations worldwide</p>
      </div>

      <div className="glass-card" style={{ padding: '2.5rem', marginBottom: '4rem' }}>
        {error && <div className="error-banner">{error}</div>}
        
        {loading ? (
          <LoadingSpinner />
        ) : (
          <form onSubmit={handleSearch}>
            <div className="search-grid">
              <div>
                <label className="search-label">From</label>
                <div style={{ position: 'relative' }}>
                  <i className="fas fa-plane-departure" style={{ position: 'absolute', top: '16px', left: '16px', color: '#3b82f6' }}></i>
                  <select 
                    className="input-field" 
                    style={{ paddingLeft: '40px', appearance: 'none' }}
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                    required
                  >
                    <option value="">Select Origin</option>
                    {airports.map(a => (
                      <option key={a.iata} value={a.iata}>{a.iata} {a.city ? `- ${a.city}` : ''}</option>
                    ))}
                  </select>
                  <i className="fas fa-chevron-down" style={{ position: 'absolute', top: '16px', right: '16px', color: '#64748b', pointerEvents: 'none' }}></i>
                </div>
              </div>

              <div>
                <label className="search-label">To</label>
                <div style={{ position: 'relative' }}>
                  <i className="fas fa-plane-arrival" style={{ position: 'absolute', top: '16px', left: '16px', color: '#3b82f6' }}></i>
                  <select 
                    className="input-field" 
                    style={{ paddingLeft: '40px', appearance: 'none' }}
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    required
                  >
                    <option value="">Select Destination</option>
                    <option value="BOM">BOM - Mumbai</option>
                    <option value="DEL">DEL - Delhi</option>
                    <option value="BLR">BLR - Bangalore</option>
                    <option value="MAA">MAA - Chennai</option>
                  </select>
                  <i className="fas fa-chevron-down" style={{ position: 'absolute', top: '16px', right: '16px', color: '#64748b', pointerEvents: 'none' }}></i>
                </div>
              </div>

              <div>
                <label className="search-label">Departure Date</label>
                <div style={{ position: 'relative' }}>
                  <input 
                    type="date" 
                    className="input-field" 
                    min={today}
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', paddingBottom: '2px' }}>
                <div style={{ display: 'flex', background: 'rgba(255,255,255,0.05)', borderRadius: '10px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
                  {['economy', 'business', 'first'].map(cls => (
                    <button
                      key={cls}
                      type="button"
                      className={`class-btn ${seatClass === cls ? 'active' : ''}`}
                      onClick={() => setSeatClass(cls)}
                    >
                      {cls}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <button type="submit" className="btn-primary w-full mt-8" style={{ fontSize: '1.125rem', padding: '16px' }}>
              <i className="fas fa-search" style={{ marginRight: '0.5rem' }}></i> Search Flights
            </button>
          </form>
        )}
      </div>

      <div className="mt-12">
        <h2 style={{ fontSize: '1.5rem', color: 'white', marginBottom: '2rem', fontWeight: 600 }}>Popular Routes</h2>
        <div className="grid-cards">
          {[
            { src: 'DEL', dest: 'BOM', city: 'Mumbai' },
            { src: 'BOM', dest: 'MAA', city: 'Chennai' },
            { src: 'BLR', dest: 'DEL', city: 'Delhi' },
            { src: 'DEL', dest: 'BLR', city: 'Bangalore' }
          ].map((route, i) => (
            <div key={i} className="glass-card" style={{ padding: '1.5rem', transition: 'transform 0.3s' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'white' }}>{route.src}</span>
                <i className="fas fa-plane" style={{ color: '#3b82f6' }}></i>
                <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'white' }}>{route.dest}</span>
              </div>
              <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '1.5rem' }}>To {route.city}</p>
              <button onClick={() => handleQuickSearch(route.src, route.dest)} className="btn-secondary w-full" style={{ padding: '8px' }}>
                Search Now
              </button>
            </div>
          ))}
        </div>
      </div>

      <style>
        {`
          .search-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
          }
          .search-label {
            display: block;
            color: #cbd5e1;
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
            font-weight: 500;
          }
          .class-btn {
            flex: 1;
            background: transparent;
            border: none;
            color: #94a3b8;
            padding: 12px;
            cursor: pointer;
            text-transform: capitalize;
            font-weight: 500;
            transition: all 0.2s;
          }
          .class-btn:hover {
            color: white;
            background: rgba(255,255,255,0.05);
          }
          .class-btn.active {
            background: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
          }
          .grid-cards {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 1.5rem;
          }
          @media (max-width: 1024px) {
            .search-grid { grid-template-columns: 1fr 1fr; }
          }
          @media (max-width: 640px) {
            .search-grid { grid-template-columns: 1fr; }
          }
        `}
      </style>
    </div>
  );
};

export default FlightSearchPage;
