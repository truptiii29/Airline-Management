import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';

const PaymentPage = () => {
  const navigate = useNavigate();
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [upiId, setUpiId] = useState('');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  
  const [passengers, setPassengers] = useState([{ id: 1, name: '', age: '', gender: 'Male', phone: '' }]);
  
  // Get booking details from session storage
  const bookingDetails = JSON.parse(sessionStorage.getItem('bookingDetails') || '{}');
  
  // Refresh seat lock when payment page loads
  useEffect(() => {
    if (bookingDetails.flight && bookingDetails.seat) {
      try {
        api.post('/seats/lock', {
          flight_id: parseInt(bookingDetails.flight.id || bookingDetails.flight.flight_id),
          seat_number: bookingDetails.seat.seat_number
        }).catch(err => {
          console.warn('Could not refresh seat lock:', err.message);
          // If lock refresh fails, still allow payment to proceed
          // The backend will validate the lock again during booking creation
        });
      } catch (err) {
        console.warn('Error refreshing seat lock:', err);
      }
    }
  }, []);
  
  if (!bookingDetails.flight || !bookingDetails.seat) {
    return (
      <div className="flex-col items-center justify-center text-center p-12">
        <h2 className="text-2xl text-white mb-4">No Booking Details Found</h2>
        <button onClick={() => navigate('/flights')} className="btn-primary">Return to Flight Search</button>
      </div>
    );
  }

  const { flight, seat, price } = bookingDetails;
  
  const user = JSON.parse(localStorage.getItem('user')) || {};
  const PassengerName = user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : 'Passenger';


  const totalPrice = price * passengers.length;

  const handleAddPassenger = () => {
    if (passengers.length < 3) {
      setPassengers([...passengers, { id: passengers.length + 1, name: '', age: '', gender: 'Male', phone: '' }]);
    }
  };

  const handlePassengerChange = (index, field, value) => {
    const updated = [...passengers];
    updated[index][field] = value;
    setPassengers(updated);
  };

  const handlePayment = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      // Validate passenger details first
      if (!passengers[0].name || !passengers[0].age || !passengers[0].phone) {
        setError('Please fill in all passenger details');
        setProcessing(false);
        return;
      }

      // 1. Create Booking first
      const bookingResp = await api.post('/bookings/', {
        flight_id: parseInt(flight.id || flight.flight_id),
        seat_number: seat.seat_number,
        seat_class: seat.seat_class.toLowerCase()
      });
      
      const bookingId = bookingResp.data.data.booking_id;
      
      // 2. Validate Payment Method
      if (paymentMethod === 'upi' && !upiId.trim()) {
        setError('UPI ID is required for UPI payments');
        setProcessing(false);
        return;
      }

      console.log('Initiating payment for booking ID:', bookingId);
      console.log('Payment Method:', paymentMethod);
      console.log('UPI ID:', paymentMethod === 'upi' ? upiId : 'N/A');
      
      // 3. Process Payment
      const paymentResponse = await fetch('http://127.0.0.1:5003/api/v1/payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          payment_method: paymentMethod === 'upi' ? 'upi' : paymentMethod.toUpperCase(),
          upi_id: paymentMethod === 'upi' ? upiId : '',
          amount: totalPrice,
          booking_id: bookingId
        })
      });
      
      const paymentData = await paymentResponse.json();
      console.log('Payment Response:', paymentData);
      
      if (!paymentData.success) {
        throw new Error(paymentData.message || paymentData.error || 'Payment processing failed');
      }
      
      const transactionId = paymentData?.data?.transaction_id || paymentData?.transaction_id || `MOCK_TXN_${Date.now()}`;

      console.log('✅ Payment Successful!');
      console.log('Transaction ID:', transactionId);
      console.log('Booking ID:', bookingId);

      // 4. Clear session and navigate to success
      sessionStorage.removeItem('bookingDetails');
      sessionStorage.removeItem('currentFlight');
      sessionStorage.removeItem('selectedClass');
      
      navigate('/booking-success', { 
        state: { 
          booking: { 
            ...bookingResp.data.data, 
            flight,
            passengers: passengers[0]
          },
          transactionId,
          paymentMethod
        } 
      });

    } catch (err) {
      console.error('Payment Error:', err);
      setError(err.message || err.response?.data?.error?.message || 'Payment processing failed. Please try again.');
      setProcessing(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ padding: '3rem 1rem', maxWidth: '1000px', margin: '0 auto' }}>
      
      <div className="payment-grid" style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.5fr) minmax(0, 1fr)', gap: '2rem' }}>
        
        {/* Left Col: Details & Payment */}
        <div>
          
          <h2 style={{ fontSize: '1.5rem', color: 'white', marginBottom: '1.5rem', fontWeight: 600 }}>Passenger Details</h2>
          
          <div className="glass-card" style={{ padding: '2rem', marginBottom: '2.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <span style={{ color: '#cbd5e1' }}>Total Passengers: <strong>{passengers.length}</strong> (Max 3)</span>
              {passengers.length < 3 && (
                <button type="button" onClick={handleAddPassenger} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.875rem' }}>
                  <i className="fas fa-plus"></i> Add Passenger
                </button>
              )}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              {passengers.map((p, idx) => (
                <div key={p.id} style={{ borderTop: idx > 0 ? '1px solid rgba(255,255,255,0.1)' : 'none', paddingTop: idx > 0 ? '1.5rem' : '0' }}>
                  <h4 style={{ color: '#3b82f6', marginBottom: '1rem', fontWeight: 600 }}>Passenger {idx + 1} of {passengers.length} {idx === 0 && '(Primary)'}</h4>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1rem' }}>
                    <div>
                      <label style={{ display: 'block', color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Full Name</label>
                      <input type="text" className="input-field" placeholder="John Doe" required value={p.name} onChange={(e) => handlePassengerChange(idx, 'name', e.target.value)} />
                    </div>
                    <div>
                      <label style={{ display: 'block', color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Phone Number</label>
                      <input type="tel" className="input-field" placeholder="+1234567890" required value={p.phone} onChange={(e) => handlePassengerChange(idx, 'phone', e.target.value)} />
                    </div>
                  </div>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div>
                      <label style={{ display: 'block', color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Age</label>
                      <input type="number" className="input-field" placeholder="30" required min="1" value={p.age} onChange={(e) => handlePassengerChange(idx, 'age', e.target.value)} />
                    </div>
                    <div>
                      <label style={{ display: 'block', color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Gender</label>
                      <select className="input-field" required value={p.gender} onChange={(e) => handlePassengerChange(idx, 'gender', e.target.value)}>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>


          <h2 style={{ fontSize: '1.5rem', color: 'white', marginBottom: '1.5rem', fontWeight: 600 }}>Select Payment Method</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem', marginBottom: '2.5rem' }}>
            {[
              { id: 'card', icon: 'fa-credit-card', label: 'Credit Card' },
              { id: 'debit', icon: 'fa-credit-card', label: 'Debit Card' },
              { id: 'upi', icon: 'fa-qrcode', label: 'UPI' },
              { id: 'netbanking', icon: 'fa-university', label: 'Net Banking' }
            ].map(method => (
               <div 
                 key={method.id}
                 onClick={() => setPaymentMethod(method.id)}
                 className={`glass-card flex-col items-center justify-center cursor-pointer transition-all ${paymentMethod === method.id ? 'active-method' : ''}`}
                 style={{ 
                   padding: '1.5rem 1rem', 
                   cursor: 'pointer',
                   border: paymentMethod === method.id ? '2px solid #3b82f6' : '1px solid rgba(255,255,255,0.1)',
                   boxShadow: paymentMethod === method.id ? '0 0 15px rgba(59,130,246,0.3)' : 'none',
                   transform: paymentMethod === method.id ? 'translateY(-2px)' : 'none'
                 }}
               >
                 <i className={`fas ${method.icon}`} style={{ fontSize: '1.5rem', color: paymentMethod === method.id ? '#3b82f6' : '#94a3b8', marginBottom: '0.75rem' }}></i>
                 <span style={{ color: paymentMethod === method.id ? 'white' : '#cbd5e1', fontWeight: 500, fontSize: '0.875rem' }}>{method.label}</span>
               </div>
            ))}
          </div>

          <div className="glass-card" style={{ padding: '2rem' }}>
            <h3 style={{ color: 'white', marginBottom: '1.5rem', fontSize: '1.125rem' }}>Payment Details</h3>
            
            {error && <div className="error-banner">{error}</div>}

            <form onSubmit={handlePayment}>
              {paymentMethod === 'upi' && (
                <div className="animate-fade-in" style={{ marginBottom: '1.5rem' }}>
                  <label style={{ display: 'block', color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                    UPI ID <span style={{ color: '#f59e0b' }}>*</span>
                  </label>
                  <input 
                    type="text" 
                    className="input-field" 
                    placeholder="e.g., yourname@paytm, phone@okhdfcbank" 
                    required 
                    value={upiId} 
                    onChange={(e) => setUpiId(e.target.value)}
                    pattern="[a-zA-Z0-9._\-]+@[a-zA-Z]+"
                  />
                  <p style={{ color: '#94a3b8', fontSize: '0.75rem', marginTop: '0.5rem' }}>
                    💡 Demo: Use any UPI format like demo@upi, test@okhdfcbank, or your@paytm
                  </p>
                </div>
              )}

              {(paymentMethod === 'card' || paymentMethod === 'debit') && (
                <div className="animate-slide-in">
                  <div style={{ marginBottom: '1.5rem' }}>
                     <label style={{ display: 'block', color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Card Number</label>
                    <div style={{ position: 'relative' }}>
                      <i className="fas fa-credit-card" style={{ position: 'absolute', top: '16px', left: '16px', color: '#64748b' }}></i>
                      <input type="text" className="input-field" placeholder="0000 0000 0000 0000" style={{ paddingLeft: '40px' }} required />
                    </div>
                  </div>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
                    <div>
                      <label style={{ display: 'block', color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Expiry Date</label>
                      <input type="text" className="input-field" placeholder="MM/YY" required />
                    </div>
                    <div>
                      <label style={{ display: 'block', color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '0.5rem' }}>CVV</label>
                      <input type="text" className="input-field" placeholder="123" maxLength="3" required />
                    </div>
                  </div>
                  
                  <div style={{ marginBottom: '1.5rem' }}>
                    <label style={{ display: 'block', color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Name on Card</label>
                    <input type="text" className="input-field" placeholder="J. Doe" required />
                  </div>
                </div>
              )}

              {paymentMethod === 'netbanking' && (
                <div className="animate-fade-in" style={{ marginBottom: '1.5rem' }}>
                  <label style={{ display: 'block', color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Select Bank</label>
                  <select className="input-field" required>
                    <option value="">Choose your bank</option>
                    <option value="sbi">SBI</option>
                    <option value="hdfc">HDFC</option>
                    <option value="icici">ICICI</option>
                    <option value="axis">Axis Bank</option>
                  </select>
                </div>
              )}

              <button 
                type="submit" 
                className="btn-primary w-full" 
                style={{ padding: '16px', fontSize: '1.125rem', marginTop: '1rem', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.75rem' }}
                disabled={processing}
              >
                {processing ? (
                  <>
                    <i className="fas fa-spinner fa-spin"></i> Processing Payment...
                  </>
                ) : (
                  <>
                    <i className="fas fa-lock"></i> Pay ₹{totalPrice} Securely
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Right Col: Order Summary */}
        <div>
          <div className="glass-card" style={{ padding: '2rem', position: 'sticky', top: '100px' }}>
            <h3 style={{ color: 'white', marginBottom: '1.5rem', fontSize: '1.25rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem' }}>Booking Summary</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Flight</span>
                <span style={{ color: 'white', fontWeight: 500 }}>{flight.flight_number}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Route</span>
                <span style={{ color: 'white', fontWeight: 500 }}>{flight.source?.iata || flight.source_iata || flight.source} → {flight.destination?.iata || flight.destination_iata || flight.destination}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Date</span>
                <span style={{ color: 'white', fontWeight: 500 }}>{new Date(flight.departure_time).toLocaleDateString()}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Passenger</span>
                <span style={{ color: 'white', fontWeight: 500 }}>{PassengerName}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', background: 'rgba(59, 130, 246, 0.1)', padding: '8px 12px', borderRadius: '8px' }}>
                <span style={{ color: '#3b82f6', fontWeight: 500 }}>Seat {seat.seat_number}</span>
                <span style={{ color: 'white', textTransform: 'capitalize' }}>{seat.seat_class}</span>
              </div>
            </div>

            <div style={{ borderTop: '2px dashed rgba(255,255,255,0.1)', paddingTop: '1.5rem', marginTop: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ color: '#94a3b8' }}>Base Fare (x{passengers.length})</span>
                <span style={{ color: 'white' }}>₹{totalPrice}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ color: '#94a3b8' }}>Taxes & Fees</span>
                <span style={{ color: 'white' }}>₹0</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                <span style={{ color: 'white', fontSize: '1.125rem', fontWeight: 600 }}>Total Amount</span>
                <span className="gradient-text" style={{ fontSize: '1.5rem', fontWeight: 800 }}>₹{totalPrice}</span>
              </div>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', marginTop: '1.5rem', padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              <i className="fas fa-shield-check" style={{ color: '#10b981', marginTop: '4px' }}></i>
              <p style={{ color: '#10b981', fontSize: '0.75rem', lineHeight: 1.4 }}>
                Your payment information is encrypted and securely processed. We do not store your card details.
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <style>
        {`
          @media (max-width: 800px) {
            .payment-grid {
              grid-template-columns: 1fr !important;
            }
          }
        `}
      </style>
    </div>
  );
};

export default PaymentPage;
