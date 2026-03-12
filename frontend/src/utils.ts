import { DriverSessionResult } from "./types";

export const formatLapTime = (time: number) => {
	const minutes = Math.floor(time / 60);
	const seconds = (time % 60).toFixed(3);
	return `${minutes}:${seconds.padStart(6, "0")}`;
};

export const formatTime = (driver: DriverSessionResult): string => {
	if (driver.time == null) {
		if (driver.status && driver.status !== "Finished") {
			return driver.status;
		}
		return "—";
	}

	if (driver.position === 1) {
		const minutes = driver.time / 60;

		if (minutes < 3) {
			// Qualifying-style lap (under 3 min) → mm:ss.sss
			const wholeMinutes = Math.floor(minutes);
			const seconds = driver.time % 60;
			return `${wholeMinutes}:${seconds.toFixed(3).padStart(6, "0")}`;
		} else {
			// Race duration → h:mm:ss
			const hours = Math.floor(driver.time / 3600);
			const mins = Math.floor((driver.time % 3600) / 60);
			const secs = Math.floor(driver.time % 60);
			return `${hours}:${mins.toString().padStart(2, "0")}:${secs
				.toString()
				.padStart(2, "0")}`;
		}
	} else {
		// For non-P1 drivers, time is gap to leader in seconds
		return `+${driver.time.toFixed(3)}s`;
	}
};
