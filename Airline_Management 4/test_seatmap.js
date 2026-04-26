const fs = require('fs');

const responseData = {
    "first": [
      {
        "is_aisle": false,
        "is_emergency_exit": true,
        "is_window": true,
        "seat_number": "14A"
      },
      {
        "is_aisle": false,
        "is_emergency_exit": true,
        "is_window": true,
        "seat_number": "14D"
      }
    ],
    "economy": [
      {
        "is_aisle": false,
        "is_emergency_exit": true,
        "is_window": true,
        "seat_number": "10F"
      }
    ]
};

const seatsData = responseData;

const renderSeatClass = (className, seats) => {
    if (!seats || seats.length === 0) return null;

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

    sortedRowNums.forEach(rowNum => {
        const rowSeats = rows[rowNum];
        
        const renderCol = (colString) => {
           const seat = rowSeats.find(s => s.seat_number.endsWith(colString));
           if (seat) return;
        };

        leftCols.forEach(c => renderCol(c));
        rightCols.forEach(c => renderCol(c));
    });
};

['first', 'business', 'economy'].forEach(c => {
    renderSeatClass(c, seatsData[c]);
});

console.log("No TypeError thrown out of renderSeatClass.");
