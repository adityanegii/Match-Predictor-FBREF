'use client'
import styles from '../styles/Home.module.css'
import Table from '@/components/Table'
import DropDown from '@/components/DropDown'
import React, { useState } from 'react'

export default function Home() {

  const [selectedModel, setSelectedModel] = useState(null);
  const [selectedLeague, setSelectedLeague] = useState(null);

  const handleModelSelect = (selectedItem) => {
    setSelectedModel(selectedItem);
  };

  const handleLeagueSelect = (selectedItem) => {
    setSelectedLeague(selectedItem);
  };

  const trainAndPredict = () => {
    const fetchData = async () => {
      try {
          const response = await fetch('http://127.0.0.1:8080/api/train-and-predict');
          const responseData = await response.json();
          console.log(responseData.message);
      } catch (error) {
          console.error('Error fetching data: ', error);
      }
  };
  fetchData();
  }

  return (
    <div className={styles.main}>
      <div className={styles.header}>
        <div className={styles.title}>
          <h1>Match-Predictor</h1>
        </div>
        <div className={styles["options-container"]}>
          <span data={1} onClick={trainAndPredict} className={styles['train-button']}>
            Train and Predict
          </span>
        </div>
        <div className={styles["options-container"]}>
          <DropDown data={1} onSelectModel={handleModelSelect} />
        </div>
        <div className={styles["options-container"]}>
          <DropDown data={0} onSelectLeague={handleLeagueSelect} />
        </div>
      </div>

      <div className={styles.table}>
        <Table league={selectedLeague} model={selectedModel}/>
      </div>
    </div>
  )
}
