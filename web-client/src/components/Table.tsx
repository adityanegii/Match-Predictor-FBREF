import { useState, useEffect } from 'react';
import ProbabilityBar from './ProbabilityBar';

interface League {
  id: string;
}

interface Model {
  id: string;
}

interface DataItem {
  Date: string;
  Home_Team: string;
  Prob_Home_Win: number;
  Prob_Draw: number;
  Prob_Away_Win: number;
  Away_Team: string;
  Predicted_GF_Home: number;
  Predicted_GF_Away: number;
}

interface TableProps {
  league: League | null;
  model: Model | null;
}

const styles = {
    headers: 'px-4 py-3 text-left font-semibold bg-blue-950',
    cells: 'px-4 py-3 bg-gray-800',
    table: 'min-w-full table-auto border-collapse border border-gray-700',
    container: 'overflow-x-auto mt-4 p-4',
    row: 'border-t border-gray-700',
}
const Table: React.FC<TableProps> = ({ league, model }) => {
  const [data, setData] = useState<DataItem[] | null>(null);

  useEffect(() => {
    if (league != null && model != null) {
      const fetchData = async () => {
        try {
          const response = await fetch(`http://127.0.0.1:8080/api/${league.id}/${model.id}`);
          const responseData = await response.json();
          setData(responseData);
        } catch (error) {
          console.error('Error fetching data: ', error);
        }
      };
      fetchData();
    }
  }, [league, model]);

  if (league == null || model == null || data == null) {
    return (
      <div className="flex flex-col items-center justify-center">
        <h1 className="text-xl font-semibold">Select a League and Model to view predictions</h1>
      </div>
    );
  }

  if (model.id === 'RFC' || model.id === 'XGBC' || model.id === 'SVC' || model.id === 'LR' || model.id === 'Ensemble') {
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
                <td className={styles.cells}>{item.Date}</td>
                <td className={styles.cells}>{item.Home_Team}</td>
                <td className={styles.cells}>
                  <ProbabilityBar home={item.Prob_Home_Win} draw={item.Prob_Draw} away={item.Prob_Away_Win} />
                </td>
                <td className={styles.cells}>{item.Away_Team}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

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
              <td className={styles.cells}>{item.Date}</td>
              <td className={styles.cells}>{item.Home_Team}</td>
              <td className={styles.cells}>{item.Predicted_GF_Home}-{item.Predicted_GF_Away}</td>
              <td className={styles.cells}>{item.Away_Team}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Table;
