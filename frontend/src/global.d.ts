export {}

declare global {
<<<<<<< HEAD
	function __(
		text: string,
		replace?: (string | number)[],
		context?: string | null
	): string
=======
	function __(text: string): string
>>>>>>> origin/feat/Billing

	interface String {
		format(...args: any[]): string
	}
<<<<<<< HEAD

	// Set on the page by the server; absent unless the site is in read-only mode.
	interface Window {
		read_only_mode?: boolean
	}
=======
>>>>>>> origin/feat/Billing
}

declare module 'vue' {
	interface ComponentCustomProperties {
<<<<<<< HEAD
		__: (
			text: string,
			replace?: (string | number)[],
			context?: string | null
		) => string
=======
		__: (text: string) => string
>>>>>>> origin/feat/Billing
	}
}
