import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: 'calc(100vh - 80px)', position: 'relative' }}>
      <div 
        style={{ 
          position: 'absolute', 
          top: 0, left: 0, right: 0, bottom: 0, 
          backgroundImage: 'url(/airplane-bg.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          zIndex: -2 
        }}
      />
      <div 
        style={{ 
          position: 'absolute', 
          top: 0, left: 0, right: 0, bottom: 0, 
          background: 'linear-gradient(135deg, rgba(10,15,30,0.85) 0%, rgba(13,21,38,0.95) 100%)',
          zIndex: -1 
        }}
      />

      <div className="flex-col items-center justify-center text-center px-4" style={{ height: '100%', minHeight: '80vh', paddingTop: '10vh' }}>
        <div className="animate-fade-in" style={{ animationDelay: '0.1s' }}>
          <span className="glass-card" style={{ padding: '8px 16px', borderRadius: '50px', fontSize: '0.875rem', color: '#3b82f6', fontWeight: 600 }}>
            ✈️ Premium Airline Experience
          </span>
        </div>

        <h1 className="animate-fade-in" style={{ fontSize: 'clamp(40px, 5vw, 64px)', fontWeight: 800, color: 'white', lineHeight: 1.2, margin: '2rem 0 1rem', animationDelay: '0.3s' }}>
          Fly With <span className="gradient-text">Modern Airways</span>
        </h1>

        <p className="animate-fade-in" style={{ fontSize: '20px', color: '#94a3b8', fontStyle: 'italic', maxWidth: '600px', margin: '0 auto 1.5rem', animationDelay: '0.5s' }}>
          "The world is yours to explore — one flight at a time."
        </p>

        <p className="animate-fade-in" style={{ fontSize: '1rem', color: '#cbd5e1', maxWidth: '600px', margin: '0 auto 3rem', animationDelay: '0.6s' }}>
          Book flights, choose your perfect seat, and travel in comfort. Your journey begins here.
        </p>

        <div className="animate-fade-in flex justify-center gap-4 flex-wrap" style={{ animationDelay: '0.7s' }}>
          <button onClick={() => navigate('/flights')} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <i className="fas fa-search"></i> Search Flights
          </button>
          <button onClick={() => navigate('/my-bookings')} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <i className="fas fa-ticket-alt"></i> View My Bookings
          </button>
        </div>

        <div className="flex flex-wrap justify-center gap-6 mt-16 animate-fade-in" style={{ animationDelay: '0.9s', maxWidth: '1000px', margin: '4rem auto 0' }}>
          <div className="glass-card feature-card animate-float" style={{ padding: '2rem', flex: '1', minWidth: '250px', animationDelay: '0s' }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6', fontSize: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
              <i className="fas fa-route"></i>
            </div>
            <h3 style={{ color: 'white', fontSize: '1.25rem', marginBottom: '0.5rem', fontWeight: 600 }}>100+ Routes</h3>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Connecting major cities with daily direct flights.</p>
          </div>

          <div className="glass-card feature-card animate-float" style={{ padding: '2rem', flex: '1', minWidth: '250px', animationDelay: '1s' }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6', fontSize: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
              <i className="fas fa-chair"></i>
            </div>
            <h3 style={{ color: 'white', fontSize: '1.25rem', marginBottom: '0.5rem', fontWeight: 600 }}>Choose Your Seat</h3>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Economy, Business & First Class tailored for comfort.</p>
          </div>

          <div className="glass-card feature-card animate-float" style={{ padding: '2rem', flex: '1', minWidth: '250px', animationDelay: '2s' }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', fontSize: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
              <i className="fas fa-shield-alt"></i>
            </div>
            <h3 style={{ color: 'white', fontSize: '1.25rem', marginBottom: '0.5rem', fontWeight: 600 }}>Secure Booking</h3>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Safe payments and instant ticket confirmation.</p>
          </div>
        </div>
      </div>

      <style>
        {`
          .feature-card {
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
          }
          .feature-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            border-radius: 16px;
            padding: 2px;
            background: linear-gradient(135deg, rgba(59,130,246,0.5), rgba(139,92,246,0.5));
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0;
            transition: opacity 0.3s ease;
          }
          .feature-card:hover::before {
            opacity: 1;
          }
          .feature-card:hover {
            transform: translateY(-10px);
          }
        `}
      </style>
    </div>
  );
};

export default LandingPage;
