import React, { useState } from 'react';
import api from '../api/axios';

const BookingCard = ({ booking, onRefresh }) => {
  const [showConfirm, setShowConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const isConfirmed = booking.status === 'confirmed';
  const flight = booking.flight || {};
  const fDate = new Date(flight.departure_time || booking.booking_date).toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' });

  const handleConfirmCancel = async () => {
    setIsLoading(true);
    try {
      const bid = booking.booking_id || booking.id;
      // Fixed API call to PUT with required Body
      await api.put(`/bookings/${bid}/cancel`, {
        cancellation_reason: "Cancelled by passenger"
      });
      setShowConfirm(false);
      if (onRefresh) onRefresh();
    } catch (error) {
      alert(error.response?.data?.error?.message || 'Failed to cancel booking. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', position: 'relative' }}>
      
      {/* Dialog Overlay */}
      {showConfirm && (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(15, 23, 42, 0.9)', borderRadius: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', zIndex: 10, backdropFilter: 'blur(4px)', padding: '2rem', textAlign: 'center' }}>
          <i className="fas fa-exclamation-triangle" style={{ fontSize: '2rem', color: '#f59e0b', marginBottom: '1rem' }}></i>
          <h3 style={{ color: 'white', marginBottom: '0.5rem' }}>Cancel Booking</h3>
          <p style={{ color: '#cbd5e1', marginBottom: '1.5rem', maxWidth: '400px' }}>
            Are you sure you want to cancel this booking? Cancellation charges may apply.
          </p>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn-secondary" onClick={() => setShowConfirm(false)} disabled={isLoading}>
              Cancel
            </button>
            <button className="btn-primary" style={{ background: '#ef4444', borderColor: '#ef4444' }} onClick={handleConfirmCancel} disabled={isLoading}>
              {isLoading ? 'Cancelling...' : 'Confirm'}
            </button>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem' }}>
        <div>
          <span style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Booking Ref:</span>
          <span style={{ color: 'white', fontWeight: 'bold', marginLeft: '0.5rem', background: 'rgba(255,255,255,0.1)', padding: '4px 8px', borderRadius: '4px' }}>{booking.booking_reference}</span>
        </div>
        <span className={`badge ${isConfirmed ? 'badge-success' : booking.status === 'cancelled' ? 'badge-error' : 'badge-warning'}`} style={{ textTransform: 'capitalize' }}>
          {booking.status}
        </span>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2rem', alignItems: 'center' }}>
        <div style={{ flex: '1', minWidth: '200px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
            <h3 style={{ color: 'white', fontSize: '1.5rem', margin: 0 }}>{flight.source_iata || flight.source}</h3>
            <i className="fas fa-arrow-right" style={{ color: '#3b82f6' }}></i>
            <h3 style={{ color: 'white', fontSize: '1.5rem', margin: 0 }}>{flight.destination_iata || flight.destination}</h3>
          </div>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
            <i className="far fa-calendar-alt" style={{ marginRight: '0.5rem' }}></i> {fDate}
          </p>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginTop: '0.25rem' }}>
             Flight {flight.flight_number}
          </p>
        </div>

        <div style={{ flex: '1', minWidth: '150px', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Seat</span>
            <span style={{ color: 'white', fontWeight: 'bold' }}>{booking.seat_number}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Class</span>
            <span style={{ color: 'white', fontWeight: 'bold', textTransform: 'capitalize' }}>{booking.seat_class}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '0.5rem', marginTop: '0.5rem' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Amount</span>
            <span style={{ color: '#10b981', fontWeight: 'bold' }}>₹{booking.total_amount}</span>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', minWidth: '150px' }}>
          {isConfirmed && (
            <>
              <button className="btn-primary" style={{ width: '100%', padding: '8px' }} onClick={() => alert('Boarding pass mockup shown here!')}>
                <i className="fas fa-ticket-alt" style={{ marginRight: '0.5rem' }}></i> Boarding Pass
              </button>
              <button className="btn-secondary" style={{ width: '100%', padding: '8px', borderColor: '#ef4444', color: '#ef4444' }} onClick={() => setShowConfirm(true)}>
                Cancel Booking
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default BookingCard;
