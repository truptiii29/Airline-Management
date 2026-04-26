import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/axios';
import FlightCard from '../components/FlightCard';
import LoadingSpinner from '../components/LoadingSpinner';

const FlightResultsPage = () => {
  const [searchParams] = useSearchParams();
  const source = searchParams.get('source');
  const destination = searchParams.get('destination');
  const date = searchParams.get('date');
  const seatClass = searchParams.get('class') || 'economy';

  const [flights, setFlights] = useState([]);
  const [filteredFlights, setFilteredFlights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // ✅ NEW: Filter and Sort State
  const [timeFilters, setTimeFilters] = useState({
    morning: false,
    afternoon: false,
    evening: false
  });
  const [sortBy, setSortBy] = useState('');

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true);
        // Assuming search query parameters match backend expectations
        let url = `/flights/search?source=${source}&destination=${destination}&date=${date}`;
        
        try {
           const response = await api.get(url);
           const respData = response.data.data || {};
           const rawFlights = respData.results || respData.items || respData || [];
           console.log("API Response:", rawFlights); // Verify number of objects
           
           // Ensure no duplicate flights exist in array payload (unique over flight_number)
           const uniqueFlightsMap = new Map();
           rawFlights.forEach(f => uniqueFlightsMap.set(f.flight_number, f));
           const uniqueFlights = Array.from(uniqueFlightsMap.values());
           
           console.log("Unique Flights Extracted:", uniqueFlights.length);
           setFlights(uniqueFlights);
        } catch (searchErr) {
           // Fallback to get all and filter locally for demo robustness
           console.log("Search endpoint failed, falling back to all flights");
           const allResp = await api.get('/flights/');
           const allRespData = allResp.data.data || {};
           const allFlights = allRespData.results || allRespData.items || allRespData || [];
           const filtered = allFlights.filter(f => {
              const srcMatch = f.source?.iata === source || f.source === source || f.source_iata === source;
              const destMatch = f.destination?.iata === destination || f.destination === destination || f.destination_iata === destination;
              const dateMatch = f.departure_time && f.departure_time.startsWith(date);
              return srcMatch && destMatch && dateMatch;
           });
            
            // Deduplicate fallback maps purely via unique key constraints explicitly
            const uniqueFlightsMap = new Map();
            filtered.forEach(f => uniqueFlightsMap.set(f.flight_number, f));
            setFlights(Array.from(uniqueFlightsMap.values()));
        }
      } catch (err) {
        setError('Failed to fetch flight results.');
      } finally {
        setLoading(false);
      }
    };

    if (source && destination && date) {
      fetchResults();
    } else {
      setLoading(false);
    }
  }, [source, destination, date]);

  // ✅ NEW: Apply filters and sorting whenever flights, filters, or sort changes
  useEffect(() => {
    let result = [...flights];

    // Apply time filters
    const hasTimeFilter = Object.values(timeFilters).some(v => v);
    if (hasTimeFilter) {
      result = result.filter(flight => {
        const depTime = new Date(flight.departure_time);
        const hour = depTime.getHours();

        if (timeFilters.morning && hour < 12) return true;
        if (timeFilters.afternoon && hour >= 12 && hour < 18) return true;
        if (timeFilters.evening && hour >= 18) return true;
        return false;
      });
    }

    // Apply sorting
    if (sortBy === 'price-low') {
      result.sort((a, b) => {
        const priceA = a[`base_price_${seatClass}`] || 0;
        const priceB = b[`base_price_${seatClass}`] || 0;
        return priceA - priceB;
      });
    } else if (sortBy === 'price-high') {
      result.sort((a, b) => {
        const priceA = a[`base_price_${seatClass}`] || 0;
        const priceB = b[`base_price_${seatClass}`] || 0;
        return priceB - priceA;
      });
    } else if (sortBy === 'departure') {
      result.sort((a, b) => {
        const timeA = new Date(a.departure_time).getTime();
        const timeB = new Date(b.departure_time).getTime();
        return timeA - timeB;
      });
    }

    setFilteredFlights(result);
  }, [flights, timeFilters, sortBy, seatClass]);

  // Make sure we pass the selected class down via localStorage or state
  // But here we'll just store it in sessionStorage so SeatSelectionPage knows
  useEffect(() => {
     sessionStorage.setItem('selectedClass', seatClass);
  }, [seatClass]);

  const fDate = date ? new Date(date).toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' }) : '';

  // ✅ NEW: Handle filter checkbox changes
  const handleFilterChange = (filterName) => {
    setTimeFilters(prev => ({
      ...prev,
      [filterName]: !prev[filterName]
    }));
  };

  return (
    <div className="animate-fade-in" style={{ padding: '2rem 1rem', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Summary Bar */}
      <div className="glass-card" style={{ padding: '1rem 2rem', marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
        <h2 style={{ fontSize: '1.25rem', color: 'white', margin: 0, display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {source} <i className="fas fa-arrow-right" style={{ color: '#3b82f6', fontSize: '1rem' }}></i> {destination}
          <span style={{ color: '#64748b', fontSize: '1rem', marginLeft: '0.5rem', fontWeight: 400 }}>|</span>
          <span style={{ color: '#94a3b8', fontSize: '1rem', fontWeight: 400 }}>{fDate}</span>
          <span style={{ color: '#64748b', fontSize: '1rem', margin: '0 0.5rem', fontWeight: 400 }}>|</span>
          <span style={{ color: '#94a3b8', fontSize: '1rem', fontWeight: 400, textTransform: 'capitalize' }}>{seatClass}</span>
        </h2>
        {/* ✅ NEW: Show filtered count */}
        <span style={{ color: '#3b82f6', fontWeight: 600 }}>
          {filteredFlights.length} flight{filteredFlights.length !== 1 ? 's' : ''} found
        </span>
      </div>

      <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }} className="results-container">
        {/* Sidebar Filters */}
        <div className="glass-card sidebar-filters" style={{ padding: '1.5rem', width: '280px', flexShrink: 0 }}>
          <h3 style={{ color: 'white', marginBottom: '1.5rem', fontSize: '1.125rem' }}>Filters</h3>
          
          <div style={{ marginBottom: '2rem' }}>
            <h4 style={{ color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '1rem' }}>Departure Time</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {/* ✅ FIXED: Morning filter */}
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#94a3b8', cursor: 'pointer' }}>
                <input 
                  type="checkbox" 
                  checked={timeFilters.morning}
                  onChange={() => handleFilterChange('morning')}
                /> 
                Morning (Before 12 PM)
              </label>
              {/* ✅ FIXED: Afternoon filter */}
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#94a3b8', cursor: 'pointer' }}>
                <input 
                  type="checkbox"
                  checked={timeFilters.afternoon}
                  onChange={() => handleFilterChange('afternoon')}
                /> 
                Afternoon (12 PM - 6 PM)
              </label>
              {/* ✅ FIXED: Evening filter */}
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#94a3b8', cursor: 'pointer' }}>
                <input 
                  type="checkbox"
                  checked={timeFilters.evening}
                  onChange={() => handleFilterChange('evening')}
                /> 
                Evening (After 6 PM)
              </label>
            </div>
          </div>

          <div>
            <h4 style={{ color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '1rem' }}>Sort By</h4>
            {/* ✅ FIXED: Sort dropdown with proper values */}
            <select 
              className="input-field" 
              style={{ padding: '8px 12px' }}
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="">Default</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="departure">Departure: Earliest</option>
            </select>
          </div>
        </div>

        {/* Results List */}
        <div style={{ flex: '1' }}>
          {error && <div className="error-banner">{error}</div>}
          
          {loading ? (
            <LoadingSpinner />
          ) : filteredFlights.length > 0 ? (
            <>
              {filteredFlights.map(flight => (
                <FlightCard key={flight.id || flight.flight_id} flight={flight} />
              ))}
            </>
          ) : (
            <div className="glass-card flex-col items-center justify-center text-center" style={{ padding: '4rem 2rem' }}>
              <div style={{ fontSize: '4rem', color: '#1e2d4a', marginBottom: '1.5rem', position: 'relative' }}>
                <i className="fas fa-plane"></i>
                <i className="fas fa-times" style={{ position: 'absolute', right: '-10px', bottom: '-10px', fontSize: '2rem', color: '#ef4444' }}></i>
              </div>
              <h3 style={{ color: 'white', fontSize: '1.5rem', marginBottom: '0.5rem' }}>
                {flights.length === 0 ? 'No Flights Found' : 'No Flights Match Filters'}
              </h3>
              <p style={{ color: '#94a3b8' }}>
                {flights.length === 0 
                  ? "We couldn't find any flights for this route on the selected date."
                  : 'Try adjusting your filters to find more flights.'}
              </p>
              <button 
                onClick={() => Object.values(timeFilters).some(v => v) ? setTimeFilters({morning: false, afternoon: false, evening: false}) : window.history.back()} 
                className="btn-secondary" 
                style={{ marginTop: '2rem' }}
              >
                {Object.values(timeFilters).some(v => v) ? 'Clear Filters' : 'Modify Search'}
              </button>
            </div>
          )}
        </div>
      </div>

      <style>
        {`
          @media (max-width: 768px) {
            .results-container {
              flex-direction: column;
            }
            .sidebar-filters {
              width: 100% !important;
            }
          }
          input[type="checkbox"] {
            accent-color: #3b82f6;
            width: 16px;
            height: 16px;
          }
        `}
      </style>
    </div>
  );
};

export default FlightResultsPage;
