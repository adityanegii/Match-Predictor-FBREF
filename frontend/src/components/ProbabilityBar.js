import React from 'react'
import styles from '../styles/ProbabilityBar.module.css'

function ProbabilityBar( { home, draw, away }) {
    return (
        <div className={styles.percentageBar}>
            <div style={{ width: `${home}%` }} className={styles.bar1} data>
                <span className={styles.tooltip}>{home}%</span>
            </div>
            <div style={{ width: `${draw}%` }} className={styles.bar2}>
                <span className={styles.tooltip}>{draw}%</span>
            </div>
            <div style={{ width: `${away}%` }} className={styles.bar3}>
                <span className={styles.tooltip}>{away}%</span>
            </div>
        </div>
      );
}

export default ProbabilityBar