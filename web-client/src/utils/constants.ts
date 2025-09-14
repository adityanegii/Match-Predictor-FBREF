import { League, Model } from "./types";

export const LEAGUES: League[] = [
    { name: "English Premier League", id: "ENG1" },
    { name: "Ligue 1", id: "FRA1" },
    { name: "Bundesliga", id: "GER1" },
    { name: "Serie A", id: "ITA1" },
    { name: "La Liga", id: "SPA1" },
];

export const MODELS: Model[] = [
    // { name: "Random Forest Regressor", id: "RFR" },
    { name: "Random Forest Classifier", id: "RFC" },
    // { name: "XGBoost Regressor", id: "XGBR" },
    { name: "XGBoost Classifier", id: "XGBC" },
    { name: "Support Vector Classifier", id: "SVC_1v1" },
    { name: "Logistic Regression", id: "LR_1v1" },
    { name: "Ensemble Model", id: "Ensemble" },
];