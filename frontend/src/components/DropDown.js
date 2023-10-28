import React, {useState} from 'react';
import styles from '../styles/DropDown.module.css'

const leagues = [
    { name: "English Premier League", id: "ENG1" },
    { name: "Ligue 1", id: "FRA1" },
    { name: "Bundesliga", id: "GER1" },
    { name: "Serie A", id: "ITA1" },
    { name: "La Liga", id: "SPA1" },
]

const models = [
    { name: "Random Forest Regressor", id: "RFR"},
    { name: "Random Forest Classifier", id: "RFC"},
    { name: "XGBoost Regressor", id: "XGBR"},
    { name: "XGBoost Classifier", id: "XGBC" },
]
const DropDown = ({ data, onSelectLeague, onSelectModel }) => {
    const [isHovered, setIsHovered] = useState(false);
    const [League, setLeague] = useState('League');
    const [Model, setModel] = useState('Model');

    const handleMouseEnter = () => {
        setIsHovered(true);
    };

    const handleMouseLeave = () => {
        setIsHovered(false);
    };

    const handleSelectLeague = (item) => {
        onSelectLeague(item);
        setLeague(item.name);
      };
    const handleSelectModel = (item) => {
        onSelectModel(item);
        setModel(item.name);
      };
      
    if (data == 0) {
        return (
            <span
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            >
                <span className={styles.options}>
                    <span>{League}</span>
                    <img 
                    src={isHovered ? 'arrowUp.svg' : 'arrowDown.svg'}
                    alt="Image"
                    height={"15px"}
                    />
                </span>
                {isHovered && (
                    <div className={styles['dropDown-content']}>
                    {leagues.map((league) => (
                        <span
                        key={league.id}
                        onClick={() => handleSelectLeague(league)}
                        className={styles.dropdownItem}
                        >
                            {league.name}
                        </span>
                    ))}
                </div>
                )}
            </span>
        )
    } 

    return (
        <span
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        >
            <span className={styles.options}>
                <span>{Model}</span>
                <img 
                src={isHovered ? 'arrowUp.svg' : 'arrowDown.svg'}
                alt="Image"
                height={"15px"}
                />
            </span>
            {isHovered && (
                <div className={styles['dropDown-content']}>
                {models.map((model) => (
                    <span
                    key={model.id}
                    onClick={() => handleSelectModel(model)}
                    className={styles.dropdownItem}
                    >
                        {model.name}
                    </span>
                ))}
            </div>
            )}
        </span>
    )
};

export default DropDown;
