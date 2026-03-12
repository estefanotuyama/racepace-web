"use client"

import "./App.css"
import { DriverCard } from "./components/DriverCard"
import { Controls } from "./components/Controls"
import { SessionResultTable } from "./components/SessionResultTable"
import { useF1Data } from "./hooks/useF1Data"
import { LapTimeChart } from "./components/LapTimeChart"
import { ReactComponent as Logo } from "./racepace-logo.svg"
import { Toaster } from "react-hot-toast"
import WelcomeMessage from "./components/WelcomeMessage"

function App() {
	const {
		years,
		events,
		sessions,
		drivers,
		sessionResult,
		selectedYear,
		selectedEvent,
		selectedSession,
		selectedDrivers,
		driverLaps,
		teamColors,
		loading,
		errors,
		handleYearChange,
		handleEventChange,
		handleSessionChange,
		handleDriverClick,
	} = useF1Data()

	return (
		<div className="app">
			<Toaster />
			<WelcomeMessage />

			<header className="app-header">
				<div className="logo-container">
					<Logo className="logo" />
				</div>
			</header>


			<main className="main-content">

				{/* Dropdown Controls */}
				<Controls
					years={years}
					events={events}
					sessions={sessions}
					selectedYear={selectedYear}
					selectedEvent={selectedEvent}
					selectedSession={selectedSession}
					loading={loading}
					errors={errors}
					onYearChange={handleYearChange}
					onEventChange={handleEventChange}
					onSessionChange={handleSessionChange}
				/>
				<div className="drivers-results-grid">
					<div>

						{selectedSession && (
							<div className="panel">
								<h2 className="panel-header">
									Drivers in {selectedEvent?.location}, {selectedEvent?.country} {selectedYear}{" "}
									{selectedSession.session_name}
									<p>Select drivers to view and compare lap times</p>
								</h2>
								{loading.drivers && <div className="loading">Loading drivers...</div>}
								{errors.drivers && <div className="error">{errors.drivers}</div>}

								<div className="drivers-grid">
									{drivers.map((driver) => (
										<DriverCard
											key={driver.driver_number}
											driver={driver}
											isSelected={selectedDrivers.some((d) => d.driver_number === driver.driver_number)}
											onClick={handleDriverClick}
										/>
									))}
								</div>
							</div>
						)}

						{selectedDrivers.length > 0 && (
							<div className="panel">
								<LapTimeChart
									selectedDrivers={selectedDrivers}
									driverLaps={driverLaps}
									loading={loading.laps}
									error={errors.laps}
									teamColors={teamColors}
								/>
							</div>
						)}
					</div>

					{selectedSession && (
						<div className="panel">
							<h2 className="panel-header">Session Result</h2>
							<SessionResultTable
								sessionResult={sessionResult}
								loading={loading.sessionResult}
								error={errors.sessionResult}
							/>
						</div>
					)}
				</div>
			</main>
			<footer className="app-footer">
				<div>
					<p>
						RacePace is an unofficial fan project and is not associated in any way with the Formula 1 companies. All F1 related marks are trade marks of Formula One Licensing B.V.
					</p>
				</div>
			</footer>
		</div>
	)
}

export default App
