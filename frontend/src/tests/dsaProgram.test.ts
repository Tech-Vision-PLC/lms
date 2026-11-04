import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import translationPlugin from '@/translation'

const call = vi.hoisted(() => vi.fn())
vi.mock('frappe-ui', () => ({ call }))
vi.mock('@/components/Modals/ProgrammingExerciseModal.vue', () => ({
	default: {},
}))
vi.mock('@/stores/user', () => ({
	usersStore: () => ({
		userResource: { data: { name: 'student@example.com' } },
	}),
}))

import { Program } from '@/utils/program'
import { dsaProblemUrl } from '@/utils/dsa'

beforeEach(() => {
	call.mockReset()
	window.translatedMessages = {}
	translationPlugin({ config: { globalProperties: {} } })
	vi.stubGlobal('__', window.__)
})

describe('DSA lesson programming exercises', () => {
	it('saves the stable problem ID and embeds the student editor', () => {
		const program = new Program({
			data: { dsa_problem: 'problem & 1' },
			api: {},
			readOnly: true,
		})
		const wrapper = program.render()
		const frame = wrapper.querySelector('iframe')!
		expect(frame.getAttribute('src')).toBe(dsaProblemUrl('problem & 1', true))
		expect(frame.title).toBe('DSA Programming Exercise')
		expect(program.save()).toEqual({ dsa_problem: 'problem & 1' })
		expect(call).not.toHaveBeenCalled()
	})

	it('renders the attached problem title as text for instructors', async () => {
		call.mockResolvedValue({ title: '<img src=x onerror=alert(1)>' })
		const program = new Program({
			data: { dsa_problem: 'problem-1' },
			api: {},
			readOnly: false,
		})
		const wrapper = program.render()
		await flushPromises()
		expect(wrapper.textContent).toContain('<img src=x onerror=alert(1)>')
		expect(wrapper.querySelector('img')).toBeNull()
	})

	it('shows a missing-problem error without losing the saved reference', async () => {
		call.mockRejectedValue(new Error('Not found'))
		const program = new Program({
			data: { dsa_problem: 'deleted' },
			api: {},
			readOnly: false,
		})
		const wrapper = program.render()
		await flushPromises()
		expect(wrapper.textContent).toContain(
			'Could not load the attached DSA problem.',
		)
		expect(program.save()).toEqual({ dsa_problem: 'deleted' })
	})

	it('continues to render existing LMS exercise submissions', async () => {
		call.mockResolvedValue({ name: 'submission-1' })
		const program = new Program({
			data: { exercise: 'exercise-1' },
			api: {},
			readOnly: true,
		})
		const wrapper = program.render()
		await flushPromises()
		expect(wrapper.querySelector('iframe')?.getAttribute('src')).toContain(
			'programming-exercises/exercise-1/submission/submission-1',
		)
		expect(program.save()).toEqual({ exercise: 'exercise-1' })
	})
})
