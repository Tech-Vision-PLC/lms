<template>
	<ListPage
		:breadcrumbs="breadcrumbs"
		:title="__('{0} Problems').format(filtered.length)"
		layout="list"
		:columns="columns"
		:rows="filtered.slice(0, pageLength)"
		:list-options="{ selectable: false, onRowClick: openProblem }"
		:total-count="filtered.length"
		:loading="problems.loading"
		:has-next-page="filtered.length > pageLength"
		v-model:page-length="pageLength"
		empty-name="DSA Problems"
		empty-icon="lucide-code"
		@load-more="pageLength += 24"
	>
		<template #filters>
			<slot name="tabs" />
			<FormControl
				v-model="search"
				:placeholder="__('Search problems')"
				:aria-label="__('Search problems')"
			>
				<template #prefix><span class="lucide-search size-4" /></template>
			</FormControl>
			<Select
				v-model="difficulty"
				:options="difficulties"
				:placeholder="__('Difficulty')"
			/>
			<div v-if="problems.error" role="alert" class="text-sm text-ink-red-3">
				{{ __('Could not load problems.') }}
				<Button variant="ghost" @click="problems.reload()">{{
					__('Retry')
				}}</Button>
			</div>
		</template>
		<template #cell="{ column, value }">
			<span v-if="column.key === 'topics'">{{ (value || []).join(', ') }}</span>
			<span v-else>{{ value }}</span>
		</template>
	</ListPage>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Button, FormControl, createResource } from 'frappe-ui'
import ListPage from '@/components/Layouts/ListPage.vue'
import Select from '@/components/Controls/Select.vue'
import { dsaProblemUrl, type DSAProblem } from '@/utils/dsa'
import type { ListRow } from '@/types'

const search = ref('')
const difficulty = ref('')
const pageLength = ref(24)
const problems = createResource({ url: 'dsa.api.get_problems', auto: true })
const filtered = computed(() =>
	(problems.data || []).filter(
		(problem: DSAProblem) =>
			(!difficulty.value || problem.difficulty === difficulty.value) &&
			[problem.title, ...(problem.topics || [])]
				.join(' ')
				.toLowerCase()
				.includes(search.value.trim().toLowerCase())
	)
)
const openProblem = (row: ListRow) =>
	window.location.assign(dsaProblemUrl(String(row.name)))
const breadcrumbs = [
	{
		label: __('Programming Exercises'),
		route: { name: 'ProgrammingExercises' },
	},
]
const columns = [
	{ label: __('Title'), key: 'title', width: 2 },
	{ label: __('Difficulty'), key: 'difficulty', width: 1 },
	{ label: __('Topics'), key: 'topics', width: 2 },
]
const difficulties = [
	{ label: __('All Difficulties'), value: '' },
	{ label: __('Easy'), value: 'easy' },
	{ label: __('Medium'), value: 'medium' },
	{ label: __('Hard'), value: 'hard' },
]
</script>
