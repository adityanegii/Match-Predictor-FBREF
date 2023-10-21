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

  return (
    <div className={styles.main}>
      <div className={styles.header}>
        <div className={styles.title}>
          <h1>Match-Predictor</h1>
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
