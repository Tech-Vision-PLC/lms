<template>
	<Dialog
		v-model:open="show"
		:title="__('Add a programming exercise to your lesson')"
		size="xl"
		:actions="[
			{
				label: __('Save'),
				variant: 'solid',
<<<<<<< HEAD
=======
				disabled: source === 'dsa' ? !problem : !exercise,
>>>>>>> origin/feat/Billing
				onClick: () => {
					saveExercise()
				},
			},
		]"
	>
		<template #default>
<<<<<<< HEAD
			<div class="text-base">
				<Link
=======
			<div class="text-base space-y-4">
				<TabButtons
					v-if="dsaEnabled()"
					v-model="source"
					:options="[
						{ label: __('DSA Problems'), value: 'dsa' },
						{ label: __('LMS Exercises'), value: 'lms' },
					]"
				/>
				<DSAProblemPicker v-if="source === 'dsa'" v-model="problem" />
				<Link
					v-else
>>>>>>> origin/feat/Billing
					v-model="exercise"
					doctype="LMS Programming Exercise"
					:label="__('Select a Programming Exercise')"
				/>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
<<<<<<< HEAD
import { Dialog } from 'frappe-ui'
import { onMounted, nextTick, ref } from 'vue'
import Link from '@/components/Controls/Link.vue'

const show = ref(false)
const exercise = ref(null)
=======
import { Dialog, TabButtons } from 'frappe-ui'
import { onMounted, nextTick, ref } from 'vue'
import Link from '@/components/Controls/Link.vue'
import DSAProblemPicker from '@/components/Controls/DSAProblemPicker.vue'
import { dsaEnabled } from '@/utils/dsa'

const show = ref(false)
const exercise = ref(null)
const problem = ref('')
const source = ref(dsaEnabled() ? 'dsa' : 'lms')
>>>>>>> origin/feat/Billing

const props = defineProps({
	onSave: {
		type: Function,
		required: true,
	},
})

onMounted(async () => {
	await nextTick()
	show.value = true
})

const saveExercise = () => {
<<<<<<< HEAD
	props.onSave(exercise.value)
=======
	if (source.value === 'dsa') {
		if (!problem.value) return
		props.onSave({ dsa_problem: problem.value })
	} else {
		if (!exercise.value) return
		props.onSave({ exercise: exercise.value })
	}
>>>>>>> origin/feat/Billing
	show.value = false
}
</script>
