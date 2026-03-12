"use client"
import { useRef, useState, useEffect } from "react"
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceLine } from "recharts"
import ReactDOM from "react-dom"

/* ---------- Helpers ---------- */
function parseTimeToSeconds(timeInput) {
	if (!timeInput) return null
	if (typeof timeInput === "number") return timeInput
	if (typeof timeInput === "string") {
		if (timeInput === "0:00.000") return null
		const parts = timeInput.split(":")
		if (parts.length === 2) {
			const minutes = Number.parseInt(parts[0], 10) || 0
			const seconds = Number.parseFloat(parts[1]) || 0
			return minutes * 60 + seconds
		}
		const s = Number.parseFloat(timeInput)
		return Number.isNaN(s) ? null : s
	}
	return null
}
function formatSecondsToTime(seconds) {
	if (seconds == null) return "N/A"
	const m = Math.floor(seconds / 60)
	const s = (seconds % 60).toFixed(3).padStart(6, "0")
	return `${m}:${s}`
}
function getCompoundColor(compound) {
	if (!compound) return "#999999"
	const c = compound.toLowerCase()
	if (c.includes("soft")) return "#DA291C"
	if (c.includes("medium")) return "#FFCD00"
	if (c.includes("hard")) return "#F0F0F0"
	if (c.includes("intermediate")) return "#43B02A"
	if (c.includes("wet")) return "#0067A5"
	return "#999999"
}

function fallbackColors(index) {
	const colors = ["#8884d8", "#82ca9d"]
	return colors[index] || "#999999"
}

/* ---------- Custom tooltip & dot ---------- */
const CustomTooltip = ({ active, payload, bestLapSec, selectedDrivers, coordinate }) => {
	if (!active || !payload || !payload.length) return null
	const data = payload[0].payload

	const driverEntries = payload.filter((entry) => entry.value != null)

	// Calculate comparison if we have exactly 2 drivers
	let comparisonText = null
	if (driverEntries.length === 2) {
		const [driver1, driver2] = driverEntries
		const timeDiff = Math.abs(driver1.value - driver2.value)
		const fasterDriver = driver1.value < driver2.value ? driver1.name : driver2.name
		const fasterDriverLastName = fasterDriver.split(" ").pop()
		comparisonText = `${fasterDriverLastName} ${timeDiff.toFixed(3)}s faster`
	}

	const tooltipContent = (
		<div className="custom-tooltip" style={{ pointerEvents: "none" }}>
			<p className="tooltip-label">Lap {data.lap}</p>
			{driverEntries.map((entry, index) => {
				const delta = entry.value != null && bestLapSec != null ? `+${(entry.value - bestLapSec).toFixed(3)}s` : ""
				const driverKey = entry.dataKey.replace("driver_", "")
				const compound = data[`compound_${driverKey}`] || "N/A"

				return (
					<div key={index} style={{ color: entry.color }}>
						<p>
							{entry.name}: {formatSecondsToTime(entry.value)}
						</p>
						{delta && <p>Delta: {delta}</p>}
						<p>Compound: {compound}</p>
					</div>
				)
			})}
			{comparisonText && <p style={{ color: "#00C49F", fontWeight: "bold", marginTop: "4px" }}>{comparisonText}</p>}
			{<p>Speed Trap: {data.speedTrap || "N/A"} km/h</p>}
			{data.pitOut && <p style={{ color: "#82aaff" }}>Pit Out Lap</p>}
			{data.isOutlier && <p style={{ color: "#cccccc" }}>Marked as outlier</p>}
		</div>
	)

	const chartEl = document.querySelector(".lap-chart-inner")
	const chartRect = chartEl && chartEl.getBoundingClientRect()

	// compute page coordinates (fallback to coordinate values if chart rect is missing)
	const pageX = chartRect
		? Math.round(chartRect.left + (coordinate?.x ?? 0) + window.scrollX + 15)
		: Math.round((coordinate?.x ?? 0) + window.scrollX + 15)

	const pageY = chartRect
		? Math.round(chartRect.top + (coordinate?.y ?? 0) + window.scrollY - 20)
		: Math.round((coordinate?.y ?? 0) + window.scrollY - 20)

	// portal wrapper with absolute positioning
	const tooltipPortal = (
		<div
			style={{
				position: "absolute",
				left: `${pageX}px`,
				top: `${pageY}px`,
				zIndex: 2147483647,
				pointerEvents: "none",
				transition: "transform 50ms linear",
			}}
		>
			{tooltipContent}
		</div>
	)

	// mount outside the chart's SVG so it never gets clipped
	return ReactDOM.createPortal(tooltipPortal, document.body)
}

const CustomDot = (props) => {
	const { cx, cy, payload, dataKey } = props
	if (payload[dataKey] == null) return null

	const driverKey = dataKey.replace("driver_", "")
	const compound = payload[`compound_${driverKey}`]

	return (
		<circle
			cx={cx}
			cy={cy}
			r={4}
			fill={getCompoundColor(compound)}
			stroke={payload.pitOut ? "#ffffff" : "none"}
			strokeWidth={payload.pitOut ? 2 : 0}
		/>
	)
}

/* ---------- Custom Legend Component ---------- */
const CustomLegend = ({ driverData }) => {
	if (!driverData || Object.keys(driverData).length <= 1) return null

	return (
		<div className="chart-legend">
			{Object.entries(driverData).map(([driverKey, data], index) => {
				const stroke = data.driver.team_color || fallbackColors(index)
				const strokeDasharray = index === 1 ? "5 5" : "0"

				return (
					<div key={driverKey} className="legend-item">
						<svg width="25" height="3" className="legend-color">
							<line
								x1="0"
								y1="1.5"
								x2="25"
								y2="1.5"
								stroke={stroke}
								strokeWidth="2"
								strokeDasharray={strokeDasharray}
							/>
						</svg>
						<span className="legend-text">
							{data.driver.first_name} {data.driver.last_name}
						</span>
					</div>
				)
			})}
		</div>
	)
}

/* ---------- Main ---------- */
export const LapTimeChart = ({ selectedDrivers, driverLaps, loading, error, teamColors }) => {
	const outerRef = useRef(null) // stable parent (visible width)
	const [containerWidth, setContainerWidth] = useState(800)
	const [driverData, setDriverData] = useState({})

	// Toggle to exclude outliers from Y-scale (default ON)
	const [excludeOutliers, setExcludeOutliers] = useState(true)

	useEffect(() => {
		if (!selectedDrivers || selectedDrivers.length === 0) {
			setDriverData({})
			return
		}

		const newDriverData = {}
		selectedDrivers.forEach((driver) => {
			const lapData = driverLaps[driver.abbreviation]
			if (lapData && lapData.laps) {
				newDriverData[driver.abbreviation] = {
					driver,
					laps: lapData.laps.map((lap) => ({
						lap: lap.lap_number,
						timeSec: parseTimeToSeconds(lap.time),
						speedTrap: lap.speed_trap,
						compound: lap.compound,
						pitOut: lap.is_pit_out_lap,
					})),
				}
			}
		})

		setDriverData(newDriverData)
	}, [selectedDrivers, driverLaps])

	// Measure stable container width (outerRef should be .chart-content)
	useEffect(() => {
		function measure() {
			const el = outerRef.current
			if (!el) return
			const w = Math.floor(el.getBoundingClientRect().width)
			setContainerWidth(w || 800)
		}
		measure()
		window.addEventListener("resize", measure)
		return () => window.removeEventListener("resize", measure)
	}, [])

	const renderContent = () => {
		if (loading) return <div className="loading">Loading lap data...</div>
		if (error) return <div className="error">{error}</div>

		if (!selectedDrivers || selectedDrivers.length === 0) {
			return <div>Select up to 2 drivers to compare their lap times.</div>
		}

		if (Object.keys(driverData).length === 0) {
			return <div>No lap data available for selected drivers.</div>
		}

		const allLaps = new Set()
		Object.values(driverData).forEach((data) => {
			data.laps.forEach((lap) => allLaps.add(lap.lap))
		})

		const sortedLaps = Array.from(allLaps).sort((a, b) => a - b)
		const chartData = sortedLaps.map((lapNumber) => {
			const lapData = { lap: lapNumber }

			Object.entries(driverData).forEach(([driverKey, data]) => {
				const lap = data.laps.find((l) => l.lap === lapNumber)
				if (lap) {
					lapData[`driver_${driverKey}`] = lap.timeSec
					lapData[`compound_${driverKey}`] = lap.compound
					lapData.speedTrap = lap.speedTrap
					lapData.pitOut = lap.pitOut
				}
			})

			return lapData
		})

		const allValidTimes = []
		Object.values(driverData).forEach((data) => {
			data.laps.forEach((lap) => {
				if (lap.timeSec != null) allValidTimes.push(lap.timeSec)
			})
		})

		const median = (() => {
			if (!allValidTimes.length) return null
			const s = [...allValidTimes].sort((a, b) => a - b)
			const m = Math.floor(s.length / 2)
			return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2
		})()

		// Mark outliers: > median * threshold
		const OUTLIER_THRESHOLD = 1.15
		chartData.forEach((d) => {
			d.isOutlier = false
			Object.keys(driverData).forEach((driverKey) => {
				const time = d[`driver_${driverKey}`]
				if (time != null && median != null && time > median * OUTLIER_THRESHOLD) {
					d.isOutlier = true
				}
			})
		})

		const outlierCount = chartData.filter((d) => d.isOutlier).length

		// Filter data for chart rendering based on excludeOutliers toggle
		const displayData = excludeOutliers ? chartData.filter((d) => !d.isOutlier) : chartData

		const bestLapSec = allValidTimes.length ? Math.min(...allValidTimes) : null
		const bestLapData = bestLapSec
			? chartData.find((d) => Object.keys(driverData).some((driverKey) => d[`driver_${driverKey}`] === bestLapSec))
			: null
		const bestLapNumber = bestLapData ? bestLapData.lap : null

		// Compute Y domain
		const PAD = 1.0 // seconds padding
		let scaleTimes = []
		chartData.forEach((d) => {
			Object.keys(driverData).forEach((driverKey) => {
				const time = d[`driver_${driverKey}`]
				if (time != null && !(excludeOutliers && d.isOutlier)) {
					scaleTimes.push(time)
				}
			})
		})

		if (scaleTimes.length === 0) {
			scaleTimes = allValidTimes
		}

		const hasScaleTimes = scaleTimes.length > 0
		const minTime = hasScaleTimes ? Math.min(...scaleTimes) : 0
		const maxTime = hasScaleTimes ? Math.max(...scaleTimes) : 0
		const yDomain = hasScaleTimes
			? [Math.ceil(maxTime + PAD), Math.max(0, Math.floor(minTime - PAD))]
			: ["auto", "auto"]

		// Chart size logic (horizontal scrolling) - responsive to viewport
		const isMobile = containerWidth <= 768
		const isSmallPhone = containerWidth <= 360
		const POINT_SPACING = isSmallPhone ? 28 : isMobile ? 36 : 60
		const baseFill = isMobile ? 0.9 : 0.8
		const innerWidth = Math.max(POINT_SPACING * displayData.length, Math.floor(containerWidth * baseFill))
		const MAX_WIDTH = 4000
		const chartInnerWidth = Math.min(innerWidth, MAX_WIDTH)

		return (
			<>
				{/* Controls / toggle */}
				<div className="outlier-controls">
					<div className="outlier-controls-left">
						<label className="outlier-toggle-label">
							<div
								onClick={() => setExcludeOutliers((v) => !v)}
								className={`toggle-switch ${excludeOutliers ? "active" : "inactive"}`}
							>
								<div className={`toggle-switch-knob ${excludeOutliers ? "active" : "inactive"}`} />
							</div>
							Hide outliers from chart
						</label>

						<div className={`outlier-badge ${outlierCount > 0 ? "has-outliers" : "no-outliers"}`}>
							<span className="outlier-badge-dot">●</span>
							{outlierCount > 0
								? `${outlierCount} outlier${outlierCount > 1 ? "s" : ""} detected`
								: "No outliers detected"}
							<span
								className="outlier-badge-hidden"
								aria-hidden="true"
								style={{ visibility: excludeOutliers && outlierCount > 0 ? "visible" : "hidden" }}
							>
								(hidden)
							</span>
						</div>
					</div>

					<div className="outlier-threshold-info">Threshold: +15% above median</div>
				</div>

				{/* Chart note */}
				<p className="chart-note">
					{excludeOutliers
						? `Showing ${displayData.length} laps with outliers hidden. Scale optimized for regular lap times.`
						: `Showing all ${chartData.length} laps.`}{" "}
					Scroll horizontally to view all data.
				</p>

				<CustomLegend driverData={driverData} />
				<div className="lap-chart-container" style={{ overflowX: "auto", paddingTop: 12 }}>

					<div
						className="lap-chart-inner"
						style={{
							minWidth: `${chartInnerWidth}px`,
							width: `${chartInnerWidth}px`,
							display: "block",
						}}
					>
						<LineChart
							width={chartInnerWidth}
							height={isSmallPhone ? 260 : isMobile ? 300 : 460}
							data={displayData}
							margin={{ top: isMobile ? 12 : 20, right: isMobile ? 20 : 30, left: isMobile ? 32 : 40, bottom: isMobile ? 12 : 20 }}
						>
							<CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />

							<XAxis
								dataKey="lap"
								type="number"
								domain={["dataMin", "dataMax"]}
								tick={{ fill: "#A9A9A9", fontSize: 12 }}
								allowDecimals={false}
								interval={0}
								label={{ value: "Lap", position: "insideBottom", offset: 0, fill: "#A9A9A9" }}
							/>
							<YAxis
								tickFormatter={(value) => {
									if (value == null) return "N/A"
									const m = Math.floor(value / 60)
									const s = (value % 60).toFixed(1)
									return m > 0 ? `${m}:${s.padStart(4, "0")}` : `${s}s`
								}}
								tick={{ fill: "#A9A9A9", fontSize: 12 }}
								domain={yDomain}
								width={80}
								tickCount={8}
								label={{
									value: "Lap Time",
									angle: -90,
									position: "insideLeft",
									fill: "#A9A9A9",
									style: { textAnchor: "middle" },
								}}
							/>
							<Tooltip
								content={<CustomTooltip bestLapSec={bestLapSec} selectedDrivers={selectedDrivers} />}
								isAnimationActive={false}
								allowEscapeViewBox={{ x: true, y: true }}
							/>

							{bestLapNumber != null && (
								<ReferenceLine
									x={bestLapNumber}
									label={{
										value: "Best Lap",
										position: "top",
										fill: "#00C49F",
										fontSize: "12px",
										fontWeight: "500",
									}}
									stroke="#00C49F"
									strokeDasharray="3 6"
									strokeWidth={2}
								/>
							)}

							{Object.entries(driverData).map(([driverKey, data], index) => (
								<Line
									key={driverKey}
									type="linear"
									dataKey={`driver_${driverKey}`}
									stroke={data.driver.team_color || fallbackColors(index)}
									strokeWidth={2}
									strokeDasharray={index === 1 ? "5 5" : "0"}
									name={`${data.driver.first_name} ${data.driver.last_name}`}
									dot={<CustomDot />}
									connectNulls={false}
									isAnimationActive={false}
									strokeLinecap="butt"
									strokeLinejoin="miter"
								/>
							))}
						</LineChart>
					</div>
				</div>
			</>
		)
	}

	const getHeaderText = () => {
		if (!selectedDrivers || selectedDrivers.length === 0) {
			return "Lap Data Comparison"
		}
		if (selectedDrivers.length === 1) {
			return `Lap Data for ${selectedDrivers[0].first_name} ${selectedDrivers[0].last_name}`
		}
		return `Lap Data Comparison: ${selectedDrivers.map((d) => `${d.first_name} ${d.last_name}`).join(" vs ")}`
	}

	return (
		<div className="panel-lap-data">
			<h2 className="panel-header">{getHeaderText()}</h2>


			<div ref={outerRef} className="chart-content" style={{ width: "100%", overflowX: "hidden" }}>
				{renderContent()}
			</div>
		</div>
	)
}
