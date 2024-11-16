interface ProbabilityBarProps {
    home: number
    draw: number
    away: number
}
const tooltipStyle = "absolute invisible group-hover:visible w-16 text-black text-center rounded-md px-2 py-1 mt-5 opacity-75"

const ProbabilityBar = ( { home, draw, away } : ProbabilityBarProps) => {
    return (
        <div className="flex h-5 w-96">
            <div style={{ width: `${home}%` }} className="relative group bg-green-600">
                <span className={`${tooltipStyle} bg-green-400`}>{home}%</span>
            </div>
            <div style={{ width: `${draw}%` }} className="relative group bg-yellow-600">
                <span className={`${tooltipStyle} bg-yellow-400`}>{draw}%</span>
            </div>
            <div style={{ width: `${away}%` }} className="relative group bg-blue-600">
                <span className={`${tooltipStyle} bg-blue-400`}>{away}%</span>
            </div>
        </div>
      );
}

export default ProbabilityBar