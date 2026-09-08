<template>
	<div class="space-y-2">
		<Combobox
			v-model="problem"
			:label="__('Select a DSA Problem')"
			:options="options"
			:loading="problems.loading"
			:required="true"
		/>
		<div v-if="problems.error" role="alert" class="text-sm text-ink-red-3">
			{{ __('Could not load problems.') }}
			<Button variant="ghost" @click="problems.reload()">{{
				__('Retry')
			}}</Button>
		</div>
		<p
			v-else-if="!problems.loading && !options.length"
			class="text-sm text-ink-gray-5"
		>
			{{ __('No DSA problems found.') }}
		</p>
	</div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Button, Combobox, createResource } from 'frappe-ui'
import type { DSAProblem } from '@/utils/dsa'

const problem = defineModel<string>({ default: '' })
const problems = createResource({ url: 'dsa.api.get_problems', auto: true })
const options = computed(() =>
	(problems.data || []).map((row: DSAProblem) => ({
		value: row.name,
		label: row.title,
		description: [row.difficulty, ...(row.topics || [])].join(', '),
	}))
)
</script>
