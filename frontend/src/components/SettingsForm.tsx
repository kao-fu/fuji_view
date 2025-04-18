import React, { useState } from 'react';

interface Props {
  onClose: () => void;
  onSave: (settings: { year: number; month: number; day: number; hour: number }) => void;
}

const SettingsForm: React.FC<Props> = ({ onClose, onSave }) => {
  const [year, setYear] = useState(2025);
  const [month, setMonth] = useState(4);
  const [day, setDay] = useState(9);
  const [hour, setHour] = useState(17);

  const handleSave = () => {
    onSave({ year, month, day, hour });
    onClose();
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0, 0, 0, 0.5)', zIndex: 1000 }}>
      <div style={{ margin: '10% auto', padding: '1rem', backgroundColor: 'white', width: '300px', borderRadius: '8px' }}>
        <h3 style={{ color: 'black' }}>Settings</h3>
        <label style={{ color: 'black' }}>
          Year:
          <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
            {[2025].map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </label>
        <br />
        <label style={{ color: 'black' }}>
          Month:
          <select value={month} onChange={(e) => setMonth(Number(e.target.value))}>
            {Array.from({ length: 1 }, (_, i) => i + 4).map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </label>
        <br />
        <label style={{ color: 'black' }}>
          Day:
          <select value={day} onChange={(e) => setDay(Number(e.target.value))}>
            {Array.from({ length: 1 }, (_, i) => i + 9).map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>
        <br />
        <label style={{ color: 'black' }}>
          Hour:
          <select value={hour} onChange={(e) => setHour(Number(e.target.value))}>
            {Array.from({ length: 3 }, (_, i) => i + 15).map((h) => (
              <option key={h} value={h}>
                {h}
              </option>
            ))}
          </select>
        </label>
        <br />
        <button onClick={handleSave}>Save</button>
        <button onClick={onClose} style={{ marginLeft: '1rem' }}>
          Cancel
        </button>
      </div>
    </div>
  );
};

export default SettingsForm;
