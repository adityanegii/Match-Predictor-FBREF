import React, { useState } from 'react';

interface Prediction {
    Date: string;
    Home_Team: string;
    Away_Team: string;
    [key: string]: any;
}

interface PredictionViewerProps {
    leagues: string[];
    models: { name: string; type: 'classifier' | 'regressor' }[];
    apiUrl: string; // API endpoint to fetch predictions
}

export default function PredictionViewer({ leagues, models, apiUrl }: PredictionViewerProps) {
    const [selectedLeague, setSelectedLeague] = useState<string>('');
    const [selectedModel, setSelectedModel] = useState<{ name: string; type: 'classifier' | 'regressor' } | null>(null);
    const [predictions, setPredictions] = useState<Prediction[] | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    const fetchPredictions = async () => {
        if (selectedLeague && selectedModel) {
            setLoading(true);
            try {
                const response = await fetch(`${apiUrl}?league=${selectedLeague}&model=${selectedModel.name}`);
                const data = await response.json();
                setPredictions(data);
            } catch (error) {
                console.error('Error fetching predictions:', error);
            } finally {
                setLoading(false);
            }
        }
    };

    return (
        <div className="p-4">
            <h1 className="text-xl font-bold mb-4">View Predictions</h1>
            
            {/* League Selector */}
            <label className="block mb-2">Select League:</label>
            <select
                className="border p-2 rounded mb-4"
                value={selectedLeague}
                onChange={(e) => setSelectedLeague(e.target.value)}
            >
                <option value="">-- Select a League --</option>
                {leagues.map((league) => (
                    <option key={league} value={league}>
                        {league}
                    </option>
                ))}
            </select>
            
            {/* Model Selector */}
            <label className="block mb-2">Select Model:</label>
            <select
                className="border p-2 rounded mb-4"
                value={selectedModel?.name || ''}
                onChange={(e) => {
                    const model = models.find((m) => m.name === e.target.value);
                    setSelectedModel(model || null);
                }}
            >
                <option value="">-- Select a Model --</option>
                {models.map((model) => (
                    <option key={model.name} value={model.name}>
                        {model.name} ({model.type})
                    </option>
                ))}
            </select>

            {/* Fetch Predictions Button */}
            <button
                className="bg-blue-500 text-white px-4 py-2 rounded"
                onClick={fetchPredictions}
                disabled={!selectedLeague || !selectedModel || loading}
            >
                {loading ? 'Loading...' : 'View Predictions'}
            </button>

            {/* Display Predictions */}
            {predictions && (
                <div className="mt-4 p-4 border rounded bg-gray-100">
                    <h2 className="text-lg font-semibold">Predictions for {selectedLeague} - {selectedModel?.name}</h2>
                    <table className="table-auto w-full">
                        <thead>
                            <tr>
                                <th className="border px-4 py-2">Date</th>
                                <th className="border px-4 py-2">Home Team</th>
                                <th className="border px-4 py-2">Away Team</th>
                                {selectedModel?.type === 'classifier' ? (
                                    <>
                                        <th className="border px-4 py-2">Predicted Winner</th>
                                        <th className="border px-4 py-2">Prob Away Win</th>
                                        <th className="border px-4 py-2">Prob Draw</th>
                                        <th className="border px-4 py-2">Prob Home Win</th>
                                    </>
                                ) : (
                                    <>
                                        <th className="border px-4 py-2">Predicted GF Away</th>
                                        <th className="border px-4 py-2">Predicted GF Home</th>
                                    </>
                                )}
                            </tr>
                        </thead>
                        <tbody>
                            {predictions.map((prediction, index) => (
                                <tr key={index}>
                                    <td className="border px-4 py-2">{prediction.Date}</td>
                                    <td className="border px-4 py-2">{prediction.Home_Team}</td>
                                    <td className="border px-4 py-2">{prediction.Away_Team}</td>
                                    {selectedModel?.type === 'classifier' ? (
                                        <>
                                            <td className="border px-4 py-2">{prediction.Predicted_Winner}</td>
                                            <td className="border px-4 py-2">{prediction.Prob_Away_Win}</td>
                                            <td className="border px-4 py-2">{prediction.Prob_Draw}</td>
                                            <td className="border px-4 py-2">{prediction.Prob_Home_Win}</td>
                                        </>
                                    ) : (
                                        <>
                                            <td className="border px-4 py-2">{prediction.Predicted_GF_Away}</td>
                                            <td className="border px-4 py-2">{prediction.Predicted_GF_Home}</td>
                                        </>
                                    )}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
