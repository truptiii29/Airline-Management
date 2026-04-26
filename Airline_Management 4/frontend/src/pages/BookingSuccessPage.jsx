import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const BookingSuccessPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [showConfetti, setShowConfetti] = useState(true);
  
  const state = location.state;
  
  useEffect(() => {
    // Hide confetti after 5 seconds
    const timer = setTimeout(() => setShowConfetti(false), 5000);
    return () => clearTimeout(timer);
  }, []);

  if (!state || !state.booking) {
    return (
      <div className="flex-col items-center justify-center text-center p-12 min-h-screen">
        <h2 className="text-2xl text-white mb-4">No Booking Data</h2>
        <button onClick={() => navigate('/')} className="btn-primary">Return Home</button>
      </div>
    );
  }

  const { booking, transactionId } = state;
  const flight = booking.flight;
  const PassengerName = JSON.parse(localStorage.getItem('user'))?.first_name + ' ' + (JSON.parse(localStorage.getItem('user'))?.last_name || '');

  return (
    <div style={{ position: 'relative', overflow: 'hidden', minHeight: 'calc(100vh - 140px)', padding: '2rem 1rem' }}>
      
      {/* Confetti Animation */}
      {showConfetti && (
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 10 }}>
          {[...Array(50)].map((_, i) => (
            <div 
              key={i} 
              style={{
                position: 'absolute',
                left: `${Math.random() * 100}%`,
                top: '-10%',
                width: `${Math.random() * 10 + 5}px`,
                height: `${Math.random() * 10 + 5}px`,
                backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'][Math.floor(Math.random() * 5)],
                animation: `confettiFall ${Math.random() * 3 + 2}s linear forwards`,
                animationDelay: `${Math.random()}s`
              }}
            />
          ))}
        </div>
      )}

      <div className="flex-col items-center animate-slide-in" style={{ maxWidth: '800px', margin: '0 auto' }}>
        
        <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem', animation: 'pulse 2s infinite' }}>
          <i className="fas fa-check" style={{ fontSize: '2.5rem', color: '#10b981' }}></i>
        </div>
        
        <h1 className="gradient-text text-center" style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '0.5rem' }}>Booking Confirmed!</h1>
        <p style={{ color: '#94a3b8', textAlign: 'center', marginBottom: '3rem', fontSize: '1.125rem' }}>
          Your ticket has been booked successfully. Have a great journey!
        </p>

        {/* Boarding Pass Mockup */}
        <div className="boarding-pass" style={{ width: '100%', background: 'white', borderRadius: '16px', overflow: 'hidden', display: 'flex', flexDirection: 'column', position: 'relative', boxShadow: '0 20px 40px rgba(0,0,0,0.5)', filter: 'drop-shadow(0 0 10px rgba(255,255,255,0.1))' }}>
          
          {/* Top Section */}
          <div style={{ background: '#3b82f6', padding: '1.5rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'white' }}>
              <span style={{ fontSize: '1.5rem' }}>✈️</span>
              <span style={{ fontWeight: 800, fontSize: '1.25rem' }}>Modern Airways</span>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.2)', padding: '4px 12px', borderRadius: '4px', color: 'white', fontWeight: 'bold', letterSpacing: '2px' }}>
              BOARDING PASS
            </div>
          </div>

          {/* Middle Section */}
          <div style={{ padding: '2rem', display: 'flex', background: 'white', color: '#1e293b' }}>
            <div style={{ flex: '2', borderRight: '2px dashed #cbd5e1', paddingRight: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem' }}>
                <div>
                  <p style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Passenger Name</p>
                  <p style={{ fontSize: '1.25rem', fontWeight: 700, textTransform: 'uppercase' }}>{PassengerName}</p>
                </div>
                <div>
                  <p style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Booking Ref</p>
                  <p style={{ fontSize: '1.25rem', fontWeight: 700, color: '#3b82f6' }}>{booking.booking_reference}</p>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
                <div>
                  <h2 style={{ fontSize: '2.5rem', fontWeight: 800, margin: 0, lineHeight: 1 }}>{flight.source?.iata || flight.source_iata || flight.source}</h2>
                  <p style={{ color: '#64748b' }}>{flight.source?.city || 'Origin'}</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', flex: '1', margin: '0 1rem' }}>
                  <div style={{ height: '2px', background: '#e2e8f0', flex: '1' }}></div>
                  <i className="fas fa-plane" style={{ color: '#3b82f6', margin: '0 1rem', fontSize: '1.5rem' }}></i>
                  <div style={{ height: '2px', background: '#e2e8f0', flex: '1' }}></div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <h2 style={{ fontSize: '2.5rem', fontWeight: 800, margin: 0, lineHeight: 1 }}>{flight.destination?.iata || flight.destination_iata || flight.destination}</h2>
                  <p style={{ color: '#64748b' }}>{flight.destination?.city || 'Dest'}</p>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                <div>
                  <p style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase' }}>Date</p>
                  <p style={{ fontWeight: 600 }}>{new Date(flight.departure_time).toLocaleDateString([], {day:'2-digit', month:'short'})}</p>
                </div>
                <div>
                  <p style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase' }}>Time</p>
                  <p style={{ fontWeight: 600 }}>{new Date(flight.departure_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
                </div>
                <div>
                  <p style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase' }}>Class</p>
                  <p style={{ fontWeight: 600, textTransform: 'capitalize' }}>{booking.seat_class}</p>
                </div>
                <div>
                  <p style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase' }}>Flight</p>
                  <p style={{ fontWeight: 600 }}>{flight.flight_number}</p>
                </div>
              </div>
            </div>

            <div style={{ flex: '1', paddingLeft: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ background: 'rgba(59, 130, 246, 0.1)', border: '2px solid #3b82f6', borderRadius: '12px', padding: '1rem', width: '100%', textAlign: 'center', marginBottom: '1.5rem' }}>
                <p style={{ fontSize: '0.75rem', color: '#3b82f6', textTransform: 'uppercase', fontWeight: 600, marginBottom: '0.25rem' }}>Seat</p>
                <h2 style={{ fontSize: '3rem', fontWeight: 800, color: '#1e293b', margin: 0, lineHeight: 1 }}>{booking.seat_number}</h2>
              </div>
              
              {/* Fake Barcode */}
              <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: 0.8 }}>
                 <i className="fas fa-barcode" style={{ fontSize: '3rem', transform: 'scaleX(2.5)', marginBottom: '0.5rem' }}></i>
                 <p style={{ fontSize: '0.65rem', letterSpacing: '4px' }}>{transactionId || 'MODERNAIRWAYS123'}</p>
              </div>
            </div>
          </div>
          
          {/* Half circles on the sides to make it look like a ticket */}
          <div style={{ position: 'absolute', top: '72px', left: '-15px', width: '30px', height: '30px', background: '#0a0f1e', borderRadius: '50%' }}></div>
          <div style={{ position: 'absolute', top: '72px', right: '-15px', width: '30px', height: '30px', background: '#0a0f1e', borderRadius: '50%' }}></div>
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginTop: '3rem', width: '100%' }}>
          <button onClick={() => navigate('/flights')} className="btn-secondary" style={{ flex: '1' }}>Search More Flights</button>
          <button onClick={() => navigate('/my-bookings')} className="btn-primary" style={{ flex: '1' }}>View My Bookings</button>
        </div>

      </div>

      <style>
        {`
          @media (max-width: 640px) {
            .boarding-pass > div:nth-child(2) {
              flex-direction: column;
            }
            .boarding-pass > div:nth-child(2) > div:first-child {
              border-right: none;
              border-bottom: 2px dashed #cbd5e1;
              padding-right: 0;
              padding-bottom: 2rem;
              margin-bottom: 2rem;
            }
            .boarding-pass > div:nth-child(2) > div:last-child {
              padding-left: 0;
            }
          }
        `}
      </style>
    </div>
  );
};

export default BookingSuccessPage;
