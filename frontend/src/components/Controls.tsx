import { Event, F1Session } from "../types"; // Import your types

interface ControlsProps {
	years: number[];
	events: Event[];
	sessions: F1Session[];

	selectedYear: number | null;
	selectedEvent: Event | null;
	selectedSession: F1Session | null;

	loading: {
		years: boolean;
		events: boolean;
		sessions: boolean;
	};
	errors: {
		years: string;
		events: string;
		sessions: string;
	};

	onYearChange: (year: number) => void;
	onEventChange: (event: Event) => void;
	onSessionChange: (session: F1Session) => void;
}

export const Controls = ({
	years,
	events,
	sessions,
	selectedYear,
	selectedEvent,
	selectedSession,
	loading,
	errors,
	onYearChange,
	onEventChange,
	onSessionChange,
}: ControlsProps) => {
	return (
		<div className="controls">
			{/* Year Dropdown */}
			<div className="dropdown-container">
				<label htmlFor="year-select">Year</label>
				<select
					id="year-select"
					value={selectedYear || ""}
					onChange={(e) => onYearChange(Number(e.target.value))}
					disabled={loading.years}
				>
					<option value="">Select Year</option>
					{years.map((year) => (
						<option key={year} value={year}>
							{year}
						</option>
					))}
				</select>
				{loading.years && <div className="loading">Loading...</div>}
				{errors.years && <div className="error">{errors.years}</div>}
			</div>

			{/* Event Dropdown */}
			<div className="dropdown-container">
				<label htmlFor="event-select">Event</label>
				<select
					id="event-select"
					value={selectedEvent?.round_number || ""}
					onChange={(e) => {
						const event = events.find((ev) => ev.round_number === Number(e.target.value));
						if (event) onEventChange(event);
					}}
					disabled={!selectedYear || loading.events}
				>
					<option value="">Select Event</option>
					{events.map((event) => (
						<option key={event.round_number} value={event.round_number}>
							{event.location}, {event.country}
						</option>
					))}
				</select>
				{loading.events && <div className="loading">Loading...</div>}
				{errors.events && <div className="error">{errors.events}</div>}
			</div>

			{/* Session Dropdown */}
			<div className="dropdown-container">
				<label htmlFor="session-select">Session</label>
				<select
					id="session-select"
					value={selectedSession?.session_name || ""}
					onChange={(e) => {
						const session = sessions.find((s) => s.session_name === e.target.value);
						if (session) onSessionChange(session);
					}}
					disabled={!selectedEvent || loading.sessions}
				>
					<option value="">Select Session</option>
					{sessions.map((session) => (
						<option key={session.session_name} value={session.session_name}>
							{session.session_name}
						</option>
					))}
				</select>
				{loading.sessions && <div className="loading">Loading...</div>}
				{errors.sessions && <div className="error">{errors.sessions}</div>}
			</div>
		</div>
	);
};
