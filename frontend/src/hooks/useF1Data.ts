"use client"

import { useState, useEffect } from "react"
import type { Driver, F1Session, Event, SessionResultData, MultipleDriverLapsData, TeamColors } from "../types"

export const API_BASE_URL = process.env.REACT_APP_API_URL

export const useF1Data = () => {
	const [years, setYears] = useState<number[]>([])
	const [events, setEvents] = useState<Event[]>([])
	const [sessions, setSessions] = useState<F1Session[]>([])
	const [drivers, setDrivers] = useState<Driver[]>([])
	const [sessionResult, setSessionResult] = useState<SessionResultData | null>(null)
	const [teamColors, setTeamColors] = useState<TeamColors | null>(null)

	// State for selections
	const [selectedYear, setSelectedYear] = useState<number | null>(null)
	const [selectedEvent, setSelectedEvent] = useState<Event | null>(null)
	const [selectedSession, setSelectedSession] = useState<F1Session | null>(null)
	const [selectedDrivers, setSelectedDrivers] = useState<Driver[]>([])

	// State for lap data
	const [driverLaps, setDriverLaps] = useState<MultipleDriverLapsData>({})

	// Loading and error states
	const [loading, setLoading] = useState({
		years: false,
		events: false,
		sessions: false,
		drivers: false,
		laps: false,
		sessionResult: false,
		teamColors: false,
	})
	const [errors, setErrors] = useState({
		years: "",
		events: "",
		sessions: "",
		drivers: "",
		laps: "",
		sessionResult: "",
		teamColors: "",
	})

	// Fetch available years on component mount
	useEffect(() => {
		fetchYears()
		fetchTeamColors()
	}, [])

	const fetchTeamColors = async () => {
		setLoading((prev) => ({ ...prev, teamColors: true }))
		setErrors((prev) => ({ ...prev, teamColors: "" }))

		try {
			const response = await fetch(`${API_BASE_URL}/teams/`)
			if (!response.ok) throw new Error("Failed to fetch team colors")

			const data = await response.json()
			setTeamColors(data)
		} catch (error) {
			setErrors((prev) => ({ ...prev, teamColors: "Failed to load team colors" }))
		} finally {
			setLoading((prev) => ({ ...prev, teamColors: false }))
		}
	}

	const fetchYears = async () => {
		setLoading((prev) => ({ ...prev, years: true }))
		setErrors((prev) => ({ ...prev, years: "" }))

		try {
			const response = await fetch(`${API_BASE_URL}/events/years/`)
			if (!response.ok) throw new Error("Failed to fetch years")

			const data = await response.json()
			setYears(data)
		} catch (error) {
			setErrors((prev) => ({ ...prev, years: "Failed to load years" }))
		} finally {
			setLoading((prev) => ({ ...prev, years: false }))
		}
	}

	const fetchEvents = async (year: number) => {
		setLoading((prev) => ({ ...prev, events: true }))
		setErrors((prev) => ({ ...prev, events: "" }))

		try {
			const response = await fetch(`${API_BASE_URL}/events/${year}`)
			if (!response.ok) throw new Error("Failed to fetch events")

			const data = await response.json()
			if (data.length === 0 && year) {
				setErrors((prev) => ({ ...prev, events: "No events available for this year" }))
			}
			setEvents(data)
		} catch (error) {
			setErrors((prev) => ({ ...prev, events: "Failed to load events" }))
		} finally {
			setLoading((prev) => ({ ...prev, events: false }))
		}
	}

	const fetchSessions = async (year: number, roundNumber: number) => {
		setLoading((prev) => ({ ...prev, sessions: true }))
		setErrors((prev) => ({ ...prev, sessions: "" }))

		try {
			const response = await fetch(`${API_BASE_URL}/sessions/${year}/${roundNumber}`)
			if (!response.ok) throw new Error("Failed to fetch sessions")

			const data = await response.json()
			if (data.length === 0) {
				setErrors((prev) => ({ ...prev, sessions: "No sessions available for this event" }))
			}
			setSessions(data)
		} catch (error) {
			setErrors((prev) => ({ ...prev, sessions: "Failed to load sessions" }))
		} finally {
			setLoading((prev) => ({ ...prev, sessions: false }))
		}
	}

	const fetchDrivers = async (year: number, roundNumber: number, sessionName: string) => {
		setLoading((prev) => ({ ...prev, drivers: true }))
		setErrors((prev) => ({ ...prev, drivers: "" }))

		try {
			const response = await fetch(`${API_BASE_URL}/drivers/${year}/${roundNumber}/${encodeURIComponent(sessionName)}`)
			if (!response.ok) throw new Error("Failed to fetch drivers")

			const data = await response.json()
			if (data.length === 0) {
				setErrors((prev) => ({ ...prev, drivers: "No drivers available for this session" }))
			}
			setDrivers(data)
		} catch (error) {
			setErrors((prev) => ({ ...prev, drivers: "Failed to load drivers" }))
		} finally {
			setLoading((prev) => ({ ...prev, drivers: false }))
		}
	}

	const fetchDriverLaps = async (year: number, roundNumber: number, sessionName: string, driverAbbreviation: string) => {
		setLoading((prev) => ({ ...prev, laps: true }))
		setErrors((prev) => ({ ...prev, laps: "" }))

		try {
			const response = await fetch(`${API_BASE_URL}/laps/${year}/${roundNumber}/${encodeURIComponent(sessionName)}/${encodeURIComponent(driverAbbreviation)}`)
			if (!response.ok) throw new Error("Failed to fetch lap data")

			const data = await response.json()
			if (!data.laps || data.laps.length === 0) {
				setErrors((prev) => ({ ...prev, laps: "No lap data available for this driver" }))
			}

			setDriverLaps((prev) => ({
				...prev,
				[driverAbbreviation]: data,
			}))
		} catch (error) {
			setErrors((prev) => ({ ...prev, laps: "Failed to load lap data" }))
		} finally {
			setLoading((prev) => ({ ...prev, laps: false }))
		}
	}

	const fetchSessionResult = async (year: number, roundNumber: number, sessionName: string) => {
		setLoading((prev) => ({ ...prev, sessionResult: true }))
		setErrors((prev) => ({ ...prev, sessionResult: "" }))

		try {
			const response = await fetch(`${API_BASE_URL}/session_result/${year}/${roundNumber}/${encodeURIComponent(sessionName)}`)
			if (!response.ok) throw new Error("Failed to retrieve session result.")

			const data = await response.json()
			if (data.length === 0) {
				setErrors((prev) => ({ ...prev, sessionResult: "No session result available for this session" }))
			}
			setSessionResult(data)
		} catch (error) {
			setErrors((prev) => ({ ...prev, sessionResult: "Failed to load session result data" }))
		} finally {
			setLoading((prev) => ({ ...prev, sessionResult: false }))
		}
	}

	// Handle dropdown changes
	const handleYearChange = (year: number) => {
		setSelectedYear(year)
		setSelectedEvent(null)
		setSelectedSession(null)
		setSelectedDrivers([])
		setEvents([])
		setSessions([])
		setDrivers([])
		setDriverLaps({})
		fetchEvents(year)
	}

	const handleEventChange = (event: Event) => {
		setSelectedEvent(event)
		setSelectedSession(null)
		setSelectedDrivers([])
		setSessions([])
		setDrivers([])
		setDriverLaps({})
		if (selectedYear) {
			fetchSessions(selectedYear, event.round_number)
		}
	}

	const handleSessionChange = (session: F1Session) => {
		setSelectedSession(session)
		setSelectedDrivers([])
		setDrivers([])
		setDriverLaps({})

		if (selectedYear && selectedEvent) {
			fetchDrivers(selectedYear, selectedEvent.round_number, session.session_name)
			fetchSessionResult(selectedYear, selectedEvent.round_number, session.session_name)
		}
	}

	const handleDriverClick = (driver: Driver) => {
		setSelectedDrivers((prev) => {
			const isAlreadySelected = prev.some((d) => d.driver_number === driver.driver_number)

			if (isAlreadySelected) {
				const newSelection = prev.filter((d) => d.driver_number !== driver.driver_number)
				setDriverLaps((prevLaps) => {
					const newLaps = { ...prevLaps }
					delete newLaps[driver.abbreviation]
					return newLaps
				})
				return newSelection
			} else if (prev.length < 2) {
				if (selectedSession && selectedYear && selectedEvent) {
					fetchDriverLaps(selectedYear, selectedEvent.round_number, selectedSession.session_name, driver.abbreviation)
				}
				return [...prev, driver]
			} else {
				const oldestDriver = prev[0]
				setDriverLaps((prevLaps) => {
					const newLaps = { ...prevLaps }
					delete newLaps[oldestDriver.abbreviation]
					return newLaps
				})
				if (selectedSession && selectedYear && selectedEvent) {
					fetchDriverLaps(selectedYear, selectedEvent.round_number, selectedSession.session_name, driver.abbreviation)
				}
				return [prev[1], driver]
			}
		})
	}

	return {
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
	}
}
