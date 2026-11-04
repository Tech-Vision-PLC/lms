export type DSAProblem = {
	name: string
	title: string
	difficulty: string
	topics: string[]
}

export type ProgramSelection = { exercise: string } | { dsa_problem: string }

export const dsaEnabled = () =>
	Boolean((window as Window & { dsa_enabled?: boolean }).dsa_enabled)

export const dsaProblemUrl = (problem: string, embedded = false) =>
	`/dsa-practice?${new URLSearchParams({
		problem,
		...(embedded ? { embedded: '1' } : {}),
	})}`
