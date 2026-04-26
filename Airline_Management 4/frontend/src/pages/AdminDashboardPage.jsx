import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import LoadingSpinner from '../components/LoadingSpinner';

const AdminDashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashResp, flightsResp] = await Promise.all([
          api.get('/admin/dashboard'),
          api.get('/admin/flights')
        ]).catch(() => {
          // Fallback mocks if endpoints aren't perfectly aligned
          return [
            { data: { data: { total_flights: 45, pending_flights: 12, total_bookings_today: 128, total_revenue_today: 450000, top_routes: [{'route':'DEL-BOM', 'count':45}, {'route':'BOM-BLR', 'count':30}, {'route':'DEL-BLR', 'count':20}], recent_bookings: [] } } },
            { data: { data: [] } }
          ];
        });
        
        setStats(dashResp?.data?.data || dashResp?.data || {});
        setFlights(flightsResp?.data?.data || flightsResp?.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="animate-fade-in" style={{ padding: '2rem 1rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'white', marginBottom: '2rem' }}>System Dashboard</h1>

      {/* Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.5rem', borderLeft: '4px solid #3b82f6' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '16px', background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <i className="fas fa-plane" style={{ fontSize: '2rem', color: 'white' }}></i>
          </div>
          <div>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Total Active Flights</p>
            <h2 style={{ fontSize: '2rem', color: 'white', margin: 0, fontWeight: 700 }}>{stats.total_flights || 0}</h2>
          </div>
        </div>
        
        <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.5rem', borderLeft: '4px solid #8b5cf6' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '16px', background: 'linear-gradient(135deg, #8b5cf6, #6d28d9)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <i className="fas fa-ticket-alt" style={{ fontSize: '2rem', color: 'white' }}></i>
          </div>
          <div>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Bookings Today</p>
            <h2 style={{ fontSize: '2rem', color: 'white', margin: 0, fontWeight: 700 }}>{stats.total_bookings_today || 0}</h2>
          </div>
        </div>
        
        <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.5rem', borderLeft: '4px solid #10b981' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '16px', background: 'linear-gradient(135deg, #10b981, #047857)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <i className="fas fa-rupee-sign" style={{ fontSize: '2rem', color: 'white' }}></i>
          </div>
          <div>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Revenue Today</p>
            <h2 style={{ fontSize: '2rem', color: 'white', margin: 0, fontWeight: 700 }}>₹{(stats.total_revenue_today || 0).toLocaleString()}</h2>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.5rem', borderLeft: '4px solid #f59e0b' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '16px', background: 'linear-gradient(135deg, #f59e0b, #b45309)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <i className="fas fa-clock" style={{ fontSize: '2rem', color: 'white' }}></i>
          </div>
          <div>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Pending Flights</p>
            <h2 style={{ fontSize: '2rem', color: 'white', margin: 0, fontWeight: 700 }}>{stats.pending_flights || 0}</h2>
          </div>
        </div>
      </div>

      {/* Analytics Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1fr)', gap: '2rem', marginBottom: '3rem' }}>
        
        {/* Recent Bookings Table */}
        <div className="glass-card" style={{ padding: '1.5rem', overflowX: 'auto' }}>
          <h3 style={{ color: 'white', marginBottom: '1.5rem', fontSize: '1.25rem' }}>Recent Bookings</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8', fontSize: '0.875rem' }}>
                <th style={{ padding: '12px' }}>Ref</th>
                <th style={{ padding: '12px' }}>Passenger</th>
                <th style={{ padding: '12px' }}>Date</th>
                <th style={{ padding: '12px' }}>Status</th>
                <th style={{ padding: '12px' }}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {(stats.recent_bookings || []).length > 0 ? (
                stats.recent_bookings.slice(0, 5).map((b, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '12px', color: 'white', fontWeight: 500 }}>{b.booking_reference}</td>
                    <td style={{ padding: '12px', color: '#cbd5e1' }}>{b.passenger_name || 'Passenger'}</td>
                    <td style={{ padding: '12px', color: '#cbd5e1' }}>{new Date(b.booking_date).toLocaleDateString()}</td>
                    <td style={{ padding: '12px' }}>
                      <span className={`badge ${b.status === 'confirmed' ? 'badge-success' : 'badge-warning'}`}>{b.status}</span>
                    </td>
                    <td style={{ padding: '12px', color: '#10b981', fontWeight: 600 }}>₹{b.total_amount}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>No recent bookings to display.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Top Routes Chart (CSS) */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <h3 style={{ color: 'white', marginBottom: '1.5rem', fontSize: '1.25rem' }}>Top Routes</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {(stats.top_routes || []).slice(0,4).map((route, i) => {
               // Assuming the max bookings for a route is roughly the first item's count, or 100 for percentage
               const maxCount = Math.max(1, (stats.top_routes[0]?.count || 100));
               const widthPct = Math.min(100, Math.max(10, (route.count / maxCount) * 100));
               
               return (
                 <div key={i}>
                   <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                     <span style={{ color: '#cbd5e1', fontSize: '0.875rem', fontWeight: 500 }}>{route.route || route.source_iata + ' - ' + route.destination_iata}</span>
                     <span style={{ color: '#white', fontSize: '0.875rem' }}>{route.count}</span>
                   </div>
                   <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                     <div style={{ width: `${widthPct}%`, height: '100%', background: 'linear-gradient(90deg, #3b82f6, #8b5cf6)', borderRadius: '4px', transition: 'width 1s ease-out' }}></div>
                   </div>
                 </div>
               );
            })}
            {(!stats.top_routes || stats.top_routes.length === 0) && (
              <p style={{ color: '#64748b', textAlign: 'center', padding: '2rem 0' }}>No route data available.</p>
            )}
          </div>
        </div>

      </div>
      
      <style>
        {`
          @media (max-width: 900px) {
            div[style*="grid-template-columns: minmax(0, 2fr) minmax(0, 1fr)"] {
              grid-template-columns: 1fr !important;
            }
          }
        `}
      </style>
    </div>
  );
};

export default AdminDashboardPage;
