import { useState, useEffect } from 'react';
import ProbabilityBar from './ProbabilityBar';

interface League {
  id: string;
}

interface Model {
  id: string;
}

interface DataItem {
  date: string;
  home_team: string;
  home_win_prob: number;
  draw_prob: number;
  away_win_prob: number;
  away_team: string;
  predicted_GF_home: number;
  predicted_GF_away: number;
}

interface TableProps {
  league: League | null;
  model: Model | null;
}

const styles = {
  headers: 'px-4 py-3 text-left font-semibold bg-blue-950',
  cells: 'px-4 py-3 bg-gray-800',
  table: 'min-w-full table-auto border-collapse border border-gray-700 ',
  container: 'overflow-x-auto p-7 bg-gray-900 rounded-lg shadow-lg',
  row: 'border-t border-gray-700',
};

const Table: React.FC<TableProps> = ({ league, model }) => {
  const [data, setData] = useState<DataItem[] | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (league != null && model != null) {
      const fetchData = async () => {
        try {
          setMessage(null);
          setError(null);
          setData(null);
          console.log(`Fetching data for league: ${league.id}, model: ${model.id}`);
          const response = await fetch(`http://127.0.0.1:8080/api/${league.id}/${model.id}`);
          const responseData = await response.json();

          if (!response.ok) {
            // Server responded with a 4xx or 5xx
            setError(responseData.error || 'Unexpected error fetching data');
          } else if (Array.isArray(responseData)) {
            // Normal case — data received
            setData(responseData);
          } else if (responseData.message) {
            // “Please run scrape/train” case
            setMessage(responseData.message);
          } else {
            setError('Unexpected response format from server');
          }
        } catch (error) {
          console.error('Error fetching data: ', error);
          setError('Failed to connect to server');
        }
      };

      fetchData();
    }
  }, [league, model]);

  // Case 1: No selection yet
  if (!league || !model) {
    return (
      <div className="flex flex-col items-center justify-center">
        <h1 className="text-xl font-semibold">Select a League and Model to view predictions</h1>
      </div>
    );
  }

  // Case 2: Error from server
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center text-red-400">
        <h1 className="text-xl font-semibold">Error: {error}</h1>
      </div>
    );
  }

  // Case 3: No results, message from server
  if (message) {
    return (
      <div className="flex flex-col items-center justify-center text-yellow-400">
        <h1 className="text-xl font-semibold">{message}</h1>
      </div>
    );
  }

  // Case 4: Still loading
  if (data === null) {
    return (
      <div className="flex flex-col items-center justify-center">
        <h1 className="text-xl font-semibold">Loading predictions...</h1>
      </div>
    );
  }

  // Case 5: Render classification model (probabilities)
  if (['RFC', 'XGBC', 'SVC_1v1', 'LR_1v1', 'Ensemble'].includes(model.id)) {
    return (
      <div className={styles.container}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.headers}>DATE</th>
              <th className={styles.headers}>HOME TEAM</th>
              <th className={styles.headers}>WIN PROBABILITY</th>
              <th className={styles.headers}>AWAY TEAM</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={index} className={styles.row}>
                <td className={styles.cells}>{item.date}</td>
                <td className={styles.cells}>{item.home_team}</td>
                <td className={styles.cells}>
                  <ProbabilityBar home={item.home_win_prob} draw={item.draw_prob} away={item.away_win_prob} />
                </td>
                <td className={styles.cells}>{item.away_team}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // Case 6: Regression models (predicted scores)
  return (
    <div className={styles.container}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th className={styles.headers}>DATE</th>
            <th className={styles.headers}>HOME TEAM</th>
            <th className={styles.headers}>SCORE</th>
            <th className={styles.headers}>AWAY TEAM</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index} className={styles.row}>
              <td className={styles.cells}>{item.date}</td>
              <td className={styles.cells}>{item.home_team}</td>
              <td className={styles.cells}>
                {item.predicted_GF_home}-{item.predicted_GF_away}
              </td>
              <td className={styles.cells}>{item.away_team}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Table;
