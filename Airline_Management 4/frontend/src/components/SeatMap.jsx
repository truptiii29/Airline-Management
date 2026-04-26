import React from 'react';

const SeatMap = ({ seatsData, selectedSeat, onSeatSelect }) => {
  if (!seatsData || Object.keys(seatsData).length === 0) {
    return <p style={{ color: 'white', textAlign: 'center' }}>No seat map available.</p>;
  }

  const renderSeatClass = (className, seats) => {
    if (!seats || seats.length === 0) return null;

    // Group seats by row numeric prefix
    const rows = {};
    seats.forEach(seat => {
      const match = seat.seat_number.match(/^(\d+)([A-Z])$/);
      if (match) {
        const rowNum = match[1];
        if (!rows[rowNum]) rows[rowNum] = [];
        rows[rowNum].push(seat);
      }
    });

    const sortedRowNums = Object.keys(rows).sort((a, b) => parseInt(a) - parseInt(b));

    // Define columns
    let leftCols = [];
    let rightCols = [];
    if (className === 'economy') {
      leftCols = ['A', 'B', 'C'];
      rightCols = ['D', 'E', 'F'];
    } else if (className === 'business') {
      leftCols = ['A', 'C'];
      rightCols = ['D', 'F'];
    } else if (className === 'first') {
      leftCols = ['A'];
      rightCols = ['D'];
    }

    return (
      <div key={className} style={{ marginBottom: '40px', width: '100%', maxWidth: '600px', margin: '0 auto 40px auto' }}>
        <h2 style={{ color: 'white', textAlign: 'center', marginBottom: '20px', textTransform: 'uppercase', fontWeight: 'bold' }}>{className} CLASS</h2>
        
        {/* Column Headers */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '10px' }}>
          <div style={{ width: '30px' }}></div>
          <div style={{ display: 'flex', gap: '8px' }}>
            {leftCols.map(c => <div key={c} style={{ width: '36px', textAlign: 'center', color: '#9ca3af', fontWeight: 'bold' }}>{c}</div>)}
          </div>
          <div style={{ width: '30px' }}></div>
          <div style={{ display: 'flex', gap: '8px' }}>
            {rightCols.map(c => <div key={c} style={{ width: '36px', textAlign: 'center', color: '#9ca3af', fontWeight: 'bold' }}>{c}</div>)}
          </div>
          <div style={{ width: '30px' }}></div>
        </div>

        {/* Rows */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {sortedRowNums.map(rowNum => {
            const rowSeats = rows[rowNum];
            
            const renderSeatSpace = (col) => {
              const seat = rowSeats.find(s => s.seat_number.endsWith(col));
              if (seat) return renderSeat(seat);
              return <div key={col} style={{ width: '36px', height: '36px' }}></div>;
            };

            return (
              <div key={rowNum} style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <div style={{ width: '30px', textAlign: 'right', paddingRight: '10px', color: '#9ca3af', fontWeight: 'bold' }}>{rowNum}</div>
                
                <div style={{ display: 'flex', gap: '8px' }}>
                  {leftCols.map(c => renderSeatSpace(c))}
                </div>
                
                <div style={{ width: '30px' }}></div>
                
                <div style={{ display: 'flex', gap: '8px' }}>
                  {rightCols.map(c => renderSeatSpace(c))}
                </div>
                
                <div style={{ width: '30px', textAlign: 'left', paddingLeft: '10px', color: '#9ca3af', fontWeight: 'bold' }}>{rowNum}</div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderSeat = (seat) => {
    const isSelected = selectedSeat?.seat_number === seat.seat_number;
    const isBooked = seat.is_available === false;
    const isLockedByOther = seat.is_locked && !isSelected;

    let bgColor = '#1e3a5f';
    let textColor = '#93c5fd';
    let shadow = 'none';
    let cursor = 'pointer';

    if (isBooked || isLockedByOther) {
      bgColor = '#ef4444';
      textColor = 'white';
      cursor = 'not-allowed';
    } else if (isSelected) {
      bgColor = '#3b82f6';
      textColor = 'white';
      shadow = '0 0 10px #3b82f6';
    }

    return (
      <div 
        key={seat.seat_number}
        onClick={() => !isBooked && !isLockedByOther && onSeatSelect(seat)}
        style={{
          width: '36px', 
          height: '36px', 
          borderRadius: '6px', 
          backgroundColor: bgColor,
          color: textColor,
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          cursor: cursor,
          fontSize: '10px',
          fontWeight: 'bold',
          boxShadow: shadow,
          userSelect: 'none'
        }}
      >
        {seat.seat_number}
      </div>
    );
  };

  return (
    <div style={{ padding: '20px', backgroundColor: '#0f172a', borderRadius: '12px' }}>
      
      {/* Legend */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginBottom: '40px', flexWrap: 'wrap', color: 'white', fontSize: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '20px', height: '20px', backgroundColor: '#1e3a5f', borderRadius: '4px' }}></div> Available
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '20px', height: '20px', backgroundColor: '#3b82f6', borderRadius: '4px', boxShadow: '0 0 8px #3b82f6' }}></div> Selected
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '20px', height: '20px', backgroundColor: '#ef4444', borderRadius: '4px' }}></div> Booked
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {['first', 'business', 'economy'].map(c => renderSeatClass(c, seatsData[c]))}
      </div>

    </div>
  );
};

export default SeatMap;
