// Types based on API models
export interface Event {
	id: number
	round_number: number
	country: string
	location: string
	official_event_name: string
	event_name: string
	event_date: string
	event_format: string
	year: number
}

export interface F1Session {
	id: number
	session_name: string
	date: string
	round_number: number
	year: number
	f1_api_support: boolean
	event_id: number
}

export interface Driver {
	driver_number: string
	abbreviation: string
	first_name: string
	last_name: string
	full_name: string
	headshot_url: string
	team_name: string
	team_color: string
}

export interface LapData {
	lap_number: number
	time: number | null
	speed_trap: number | null
	is_pit_out_lap: boolean
	compound: string | null
}

export interface DriverLapsData {
	driver_number: string
	abbreviation: string
	first_name: string
	last_name: string
	team_name: string
	team_color: string
	headshot_url: string
	laps: LapData[]
}

export interface DriverSessionResult {
	position: number | null
	classified_position: string
	grid_position: number | null
	team_name: string
	team_color: string
	first_name: string
	last_name: string
	abbreviation: string
	q1: number | null
	q2: number | null
	q3: number | null
	time: number | null
	status: string
	points: number
	laps: number | null
}

export interface SessionResultData {
	result: DriverSessionResult[]
}

export interface MultipleDriverLapsData {
	[driverNumber: string]: DriverLapsData
}

export type TeamColors = Record<string, string>;
