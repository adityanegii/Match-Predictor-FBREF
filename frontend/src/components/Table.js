import React from 'react';
import styles from '../styles/Table.module.css'
import { useState, useEffect } from 'react';
import ProbabilityBar from './ProbabilityBar';

const Table = ({ league, model }) => {
    const [data, setData] = useState(null);

    useEffect(() => {
        if (league != null && model != null) {
            const fetchData = async () => {
                try {
                    const response = await fetch('http://127.0.0.1:8080/api/' + league.id + '/' + model.id);
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
            <div className={styles.main}> 
                <h2>
                    Select a League and Model to view predictions
                </h2>
                <img src="arrowCurved.svg" alt="italian truili" height={"500"}/>
            </div>
        )
    } else {

    if (model.id == "RFC" || model.id == "XGBC") {
        return (
            <div className={styles['table-container']}>

            <table>
            <thead>
                <tr>
                    <th>DATE</th>
                    <th>HOME TEAM</th>
                    <th>WIN PROBABILITY</th>
                    <th>AWAY TEAM</th>
                </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                  <tr key={index}>
                <td>{item.Date}</td>
                <td>{item.Home_Team}</td>
                {/* <td>Home: {item.Prob_Home_Win} --- Draw: {item.Prob_Draw} --- Away {item.Prob_Away_Win}</td> */}
                <td><ProbabilityBar home={item.Prob_Home_Win} draw={item.Prob_Draw} away={item.Prob_Away_Win}/></td>
                <td>{item.Away_Team}</td>
              </tr>
            ))}
            </tbody>
            </table>
            </div>
        )
    }

    return (
        <div className={styles['table-container']}>
        <table>
            <thead>
                <tr>
                    <th>DATE</th>
                    <th>HOME TEAM</th>
                    <th>SCORE</th>
                    <th>AWAY TEAM</th>
                </tr>
            </thead>
            <tbody>
            {data.map((item, index) => (
            <tr key={index}>
              <td>{item.Date}</td>
              <td>{item.Home_Team}</td>
              <td>{item.Predicted_GF_Home}-{item.Predicted_GF_Away}</td>
              <td>{item.Away_Team}</td>
            </tr>
          ))}
            </tbody>
        </table>
        </div>
    );
    }
};

export default Table;