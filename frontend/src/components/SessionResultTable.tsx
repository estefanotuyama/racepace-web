import { SessionResultData } from "../types"
import { formatTime } from "../utils"

interface SessionResultProps {
	sessionResult: SessionResultData | null
	loading: boolean
	error: string
}

export const SessionResultTable = ({ sessionResult, loading, error }: SessionResultProps) => {
	if (loading) {
		return <div className="loading">Loading session result...</div>
	}

	if (error) {
		return <div className="error">{error}</div>
	}

	if (!sessionResult || sessionResult.result.length === 0) {
		return null
	}

	return (
		<div className="results-table-container">
			<table className="results-table">
				<thead>
					<tr>
						<th>Pos</th>
						<th>Driver</th>
						<th>Team</th>
						<th>Gap</th>
						<th>Laps</th>
					</tr>
				</thead>
				<tbody>
					{sessionResult.result.map((driver) => (
						<tr key={driver.position}>
							<td>{driver.position}</td>
							<td>{`${driver.last_name}`}</td>
							<td>{driver.team_name}</td>
							<td>{formatTime(driver)}</td>
							<td>{driver.laps ?? 0}</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	)
}
