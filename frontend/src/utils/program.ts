import { createApp, h } from 'vue'
import { registerDirectives } from '@/directives'
import { Code } from 'lucide-vue-next'
import translationPlugin from '@/translation'
import ProgrammingExerciseModal from '@/components/Modals/ProgrammingExerciseModal.vue'
import { call } from 'frappe-ui'
import { usersStore } from '@/stores/user'
import { getLmsRoute } from '@/utils/basePath'
import { blockNotice, embedFrame } from '@/utils/blockDom'
<<<<<<< HEAD
=======
import { dsaProblemUrl, type ProgramSelection } from '@/utils/dsa'
>>>>>>> origin/feat/Billing

export class Program {
	data: any
	api: any
	readOnly: boolean
	wrapper: HTMLDivElement

	studentView: boolean

	constructor({
		data,
		api,
		readOnly,
		config,
	}: {
		data: any
		api: any
		readOnly: boolean
		config?: { studentView?: boolean }
	}) {
		this.data = data
		this.api = api
		this.readOnly = readOnly
		// The submission renders in an iframe (its own Vue app), so the
		// preview's provide/inject can't reach it. Same mechanism as the
		// assignment tool: the flag travels in the URL.
		this.studentView = Boolean(config?.studentView)
	}

	static get toolbox() {
		const app = createApp({
			render: () => h(Code, { size: 5, strokeWidth: 1.5 }),
		})
		registerDirectives(app)

		const div = document.createElement('div')
		app.mount(div)

		return {
			title: __('Programming Exercise'),
			icon: div.innerHTML,
		}
	}

	static get isReadOnlySupported() {
		return true
	}

	render() {
		this.wrapper = document.createElement('div')
<<<<<<< HEAD
		if (Object.keys(this.data).length) {
=======
		if (this.data.dsa_problem) {
			this.renderDSAProblem(this.data.dsa_problem)
		} else if (this.data.exercise) {
>>>>>>> origin/feat/Billing
			this.renderExercise(this.data.exercise)
		} else {
			this.renderModal()
		}
		return this.wrapper
	}

	renderModal() {
		if (this.readOnly) {
			return
		}
		const app = createApp(ProgrammingExerciseModal, {
<<<<<<< HEAD
			onSave: (exercise: string) => {
				this.data.exercise = exercise
				this.renderExercise(exercise)
=======
			onSave: (selection: ProgramSelection) => {
				this.data = selection
				if ('dsa_problem' in selection)
					this.renderDSAProblem(selection.dsa_problem)
				else this.renderExercise(selection.exercise)
>>>>>>> origin/feat/Billing
			},
		})
		registerDirectives(app)
		app.use(translationPlugin)
		app.mount(this.wrapper)
	}

<<<<<<< HEAD
=======
	renderDSAProblem(problem: string) {
		if (this.readOnly) {
			const frame = embedFrame(dsaProblemUrl(problem, true), {
				class: 'w-full h-[900px] border rounded-md',
				title: __('DSA Programming Exercise'),
			})
			this.wrapper.replaceChildren(...(frame ? [frame] : []))
			return
		}
		call('dsa.api.get_problem', { name: problem })
			.then((data: { title: string }) => {
				this.wrapper.replaceChildren(
					blockNotice(__('DSA Problem: {0}').format(data.title)),
				)
			})
			.catch(() => {
				this.wrapper.replaceChildren(
					blockNotice(__('Could not load the attached DSA problem.')),
				)
			})
	}

>>>>>>> origin/feat/Billing
	renderExercise(exercise: string) {
		if (this.readOnly) {
			const { userResource } = usersStore()
			call('frappe.client.get_value', {
				doctype: 'LMS Programming Exercise Submission',
				filters: {
					exercise: exercise,
					member: userResource.data?.name,
				},
				fieldname: ['name'],
			}).then((data: { name: string }) => {
				let submission = data.name || 'new'
				const studentView = this.studentView ? '&studentView=1' : ''
				const submissionPath = getLmsRoute(
<<<<<<< HEAD
					`programming-exercises/${exercise}/submission/${submission}?fromLesson=1${studentView}`
=======
					`programming-exercises/${exercise}/submission/${submission}?fromLesson=1${studentView}`,
>>>>>>> origin/feat/Billing
				)
				const frame = embedFrame(submissionPath, {
					class: 'w-full h-[900px] border rounded-md',
				})
				this.wrapper.replaceChildren(...(frame ? [frame] : []))
			})
			return
		}
		call('frappe.client.get_value', {
			doctype: 'LMS Programming Exercise',
			filters: {
				name: exercise,
			},
			fieldname: 'title',
		}).then((data: { title: string }) => {
			this.wrapper.replaceChildren(
<<<<<<< HEAD
				blockNotice(`Programming Exercise: ${data.title}`)
=======
				blockNotice(`Programming Exercise: ${data.title}`),
>>>>>>> origin/feat/Billing
			)
			return
		})
	}

	save() {
<<<<<<< HEAD
=======
		if (this.data.dsa_problem) return { dsa_problem: this.data.dsa_problem }
>>>>>>> origin/feat/Billing
		if (!this.data.exercise) return {}
		return {
			exercise: this.data.exercise,
		}
	}
}
