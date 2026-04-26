import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const FlightCard = ({ flight }) => {
  const navigate = useNavigate();
  const location = useLocation();

  // Get selected class from URL search params
  const searchParams = new URLSearchParams(location.search);
  const selectedClass = searchParams.get('class') || 'economy';

  const handleSelectSeat = () => {
    localStorage.setItem("flight", JSON.stringify(flight));
    navigate(`/flights/${flight.flight_id || flight.id}/seats`, { state: { flight } });
  };

  const depTime = new Date(flight.departure_time);
  const arrTime = new Date(flight.arrival_time);

  // ✅ Get class-specific seat count based on search selection
  const getAvailableSeats = () => {
    if (selectedClass === 'economy') return flight.available_economy;
    if (selectedClass === 'business') return flight.available_business;
    if (selectedClass === 'first') return flight.available_first;
    return flight.available_economy; // default
  };

  const availableSeats = getAvailableSeats();

  return (
    <div className="glass-card flight-card" style={{ padding: '1.5rem', marginBottom: '1.5rem', display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', transition: 'all 0.3s ease', cursor: 'default' }}>
      
      {/* Left section: Source */}
      <div style={{ flex: '1', minWidth: '150px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 700, color: 'white', margin: 0 }}>{flight.source?.iata}</h2>
        <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginTop: '0.25rem' }}>{flight.source?.city}</p>
        <p style={{ color: '#3b82f6', fontWeight: 600, marginTop: '0.5rem' }}>
          {depTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>

      {/* Center section: Duration */}
      <div style={{ flex: '1.5', minWidth: '200px', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '0 1rem' }}>
        <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '0.5rem' }}>{flight.duration_display}</p>
        <div style={{ display: 'flex', alignItems: 'center', width: '100%', gap: '0.5rem' }}>
          <div style={{ height: '2px', background: 'rgba(255,255,255,0.1)', flex: '1' }}></div>
          <i className="fas fa-plane" style={{ color: '#3b82f6', fontSize: '1.25rem' }}></i>
          <div style={{ height: '2px', background: 'rgba(255,255,255,0.1)', flex: '1', borderTop: '2px dotted rgba(255,255,255,0.2)' }}></div>
        </div>
        <span className="badge badge-success" style={{ marginTop: '0.5rem' }}>Direct</span>
      </div>

      {/* Right section: Destination */}
      <div style={{ flex: '1', minWidth: '150px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 700, color: 'white', margin: 0 }}>{flight.destination?.iata}</h2>
        <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginTop: '0.25rem' }}>{flight.destination?.city}</p>
        <p style={{ color: '#3b82f6', fontWeight: 600, marginTop: '0.5rem' }}>
          {arrTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>

      {/* Far Right section: Price & Action */}
      <div style={{ flex: '1', minWidth: '180px', display: 'flex', flexDirection: 'column', alignItems: 'center', borderLeft: '1px solid rgba(255,255,255,0.1)', paddingLeft: '1.5rem', marginTop: window.innerWidth < 768 ? '1.5rem' : '0' }}>
        <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>{flight.flight_number}</p>
        
        {flight.prices ? (
          <div style={{ fontSize: '0.875rem', color: 'white', marginTop: '0.5rem', marginBottom: '0.5rem', textAlign: 'left' }}>
             <p style={{ margin: '2px 0' }}>Economy: <span style={{color: '#3b82f6', fontWeight: 600}}>₹{flight.prices.economy}</span></p>
             <p style={{ margin: '2px 0' }}>Business: <span style={{color: '#3b82f6', fontWeight: 600}}>₹{flight.prices.business}</span></p>
             <p style={{ margin: '2px 0' }}>First: <span style={{color: '#3b82f6', fontWeight: 600}}>₹{flight.prices.first}</span></p>
          </div>
        ) : (
          <h3 className="gradient-text" style={{ fontSize: '1.75rem', fontWeight: 700, margin: '0.5rem 0 0' }}>₹{flight.price}</h3>
        )}
        
        <p style={{ color: '#64748b', fontSize: '0.75rem', marginBottom: '1rem' }}>per person</p>
        
        {/* ✅ Show class-specific available seats */}
        {availableSeats !== undefined && (
          <p style={{ color: availableSeats < 10 ? '#ef4444' : '#10b981', fontSize: '0.75rem', marginBottom: '0.5rem' }}>
            {availableSeats} {selectedClass} seats left
          </p>
        )}
        
        <button onClick={handleSelectSeat} className="btn-primary" style={{ width: '100%', padding: '10px' }}>
          Select Seat
        </button>
      </div>

      <style>
        {`
          .flight-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            border-color: rgba(59, 130, 246, 0.3);
          }
          @media (max-width: 768px) {
            .flight-card > div:last-child {
              border-left: none;
              border-top: 1px solid rgba(255,255,255,0.1);
              padding-left: 0;
              padding-top: 1.5rem;
              width: 100%;
            }
          }
        `}
      </style>
    </div>
  );
};

export default FlightCard;
