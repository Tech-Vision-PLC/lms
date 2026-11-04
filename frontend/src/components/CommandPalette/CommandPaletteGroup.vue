<template>
<<<<<<< HEAD
	<div
		v-for="result in list"
		:key="result.title"
		data-palette-group
		class="px-2.5 space-y-2"
	>
=======
	<div v-for="result in list" :key="result.title" class="px-2.5 space-y-2">
>>>>>>> origin/feat/Billing
		<div class="text-ink-gray-5 px-2">
			{{ result.title }}
		</div>
		<ul class="list-none">
			<li v-for="(item, index) in result.items" :key="index">
				<button
					type="button"
					data-palette-item
<<<<<<< HEAD
					:data-active="item.isActive ? 'true' : 'false'"
					:disabled="item.isStale"
					class="flex items-center justify-between p-2 rounded w-full text-start"
					:class="[
						item.isStale
							? 'opacity-50 cursor-default'
							: 'cursor-pointer hover:bg-surface-gray-2',
						{ 'bg-surface-gray-2': item.isActive },
					]"
					@click="emit('select', item)"
				>
					<div class="flex items-center gap-x-3">
						<span
							v-if="item.icon"
							:class="[item.icon, 'size-4 text-ink-gray-6']"
=======
					class="flex items-center justify-between p-2 rounded hover:bg-surface-gray-2 cursor-pointer w-full text-start"
					:class="{ 'bg-surface-gray-2': item.isActive }"
					@click="emit('navigateTo', item.route)"
				>
					<div class="flex items-center gap-x-3">
						<component
							v-if="item.icon"
							:is="item.icon"
							class="size-4 stroke-1.5 text-ink-gray-6"
>>>>>>> origin/feat/Billing
						/>
						<div v-safe-html:rich="item.title"></div>
					</div>
					<div v-if="item.modified" class="text-ink-gray-5">
						{{ dayjs.unix(item.modified).fromNow(true) }}
					</div>
				</button>
			</li>
		</ul>
	</div>
</template>
<script lang="ts" setup>
import { inject } from 'vue'
<<<<<<< HEAD
import type { PaletteGroup, PaletteItem } from './paletteTypes'

const dayjs = inject<any>('$dayjs')
const emit = defineEmits<{ select: [item: PaletteItem] }>()

defineProps<{
	list: PaletteGroup[]
=======

const dayjs = inject<any>('$dayjs')
const emit = defineEmits(['navigateTo'])

const props = defineProps<{
	list: Array<{
		title: string
		items: Array<{
			title: string
			route: { name: string; params?: Record<string, string> }
			icon?: any
			isActive?: boolean
			modified?: string
		}>
	}>
>>>>>>> origin/feat/Billing
}>()
</script>
