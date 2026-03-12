"use client"

import type { Driver } from "../types"

interface DriverCardProps {
	driver: Driver
	isSelected: boolean
	onClick: (driver: Driver) => void
}

export const DriverCard = ({ driver, isSelected, onClick }: DriverCardProps) => {
	return (
		<div className={`driver-card ${isSelected ? "selected" : ""}`} onClick={() => onClick(driver)}>
			<img
				src={driver.headshot_url || "/placeholder.jpeg"}
				alt={`${driver.first_name} ${driver.last_name}`}
				className="driver-image"
				onError={(e) => {
					; (e.target as HTMLImageElement).src = "/placeholder.jpeg?height=80&width=80"
				}}
			/>
			<div className="driver-info">
				<h3>
					{driver.first_name} {driver.last_name}
				</h3>
				<p className="driver-number">#{driver.driver_number}</p>
				<p className="driver-team">{driver.team_name}</p>
			</div>
		</div>
	)
}
