import styles from '../styles/Home.module.css'

export default function Home() {
  return (
    <div className={styles.main}>
      <div className={styles.header}>

        <div className={styles.title}>
          <h1>Match-Predictor</h1>
        </div>
        <div className={styles.options}>
          <h3>League</h3>
          <img src="arrowDown.svg" height={"20px"}/>
        </div>
        <div className={styles.options}>
          <h3>Model</h3>
          <img src="arrowDown.svg" height={"20px"}/>
        </div>
      </div>

      <div className={styles.table}>
        <div className={styles.headerRow}>
          <div>DATE</div>
          <div>HOME TEAM</div>
          <div>PREDICTION</div>
          <div>AWAY TEAM</div>
        </div>
      </div>
    </div>
  )
}
