import pandas as pd
import numpy as np
from data_models.Result import Result
from sqlalchemy.orm import sessionmaker
from constants import league_full
from sqlalchemy.dialects.sqlite import insert


def soft_voting(models: list[str], league: str, session: sessionmaker):
    # Load results from db
    results = session.query(Result).filter(Result.league == league_full[league]).all()
    session.close()

    if not results:
        print(f"No results found for league: {league}")
        return
    
    # Convert to DataFrame
    results_df = pd.DataFrame([res.as_dict() for res in results])
    results_df.set_index(['date', 'home_team', 'away_team', 'model_type'], inplace=True)

    # Only keep specified models
    results_df = results_df[results_df.index.get_level_values('model_type').isin(models)]
    if results_df.empty:
        print(f"No results found for specified models in league: {league}")
        return
    
    # Group by match
    grouped = results_df.groupby(level=['date', 'home_team', 'away_team'])
    ensemble_probs = grouped[['home_win_prob', 'draw_prob', 'away_win_prob']].mean()

    # Renormalize to sum to 1
    ensemble_probs = ensemble_probs.div(ensemble_probs.sum(axis=1), axis=0)
    ensemble_probs[['home_win_prob', 'draw_prob', 'away_win_prob']] *= 100
    ensemble_probs = ensemble_probs.reset_index()

    # Setup to save to Result table
    ensemble_probs['model_type'] = 'Ensemble'
    ensemble_probs['league'] = league_full[league]

    records = ensemble_probs.to_dict(orient='records')

    # Save to db
    try:
        stmt = insert(Result).values(records)

        stmt = stmt.on_conflict_do_update(
            index_elements=['date', 'home_team', 'model_type'],
            set_={
                'away_team': stmt.excluded.away_team,
                'league': stmt.excluded.league,
                'home_win_prob': stmt.excluded.home_win_prob,
                'draw_prob': stmt.excluded.draw_prob,
                'away_win_prob': stmt.excluded.away_win_prob
            }
        )

        session.execute(stmt)
        session.commit()
    except Exception as e:
        print(f"Error saving ensemble results to database for {league}:\n{e}")
        session.rollback()
        raise e