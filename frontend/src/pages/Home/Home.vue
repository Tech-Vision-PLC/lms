<template>
	<div class="w-full p-5">
		<div class="space-y-2">
			<div class="flex items-center justify-between">
				<h1 class="text-2xl-bold text-ink-gray-9">
					{{ __('Hey') }}, {{ user.data?.full_name }} 👋
				</h1>
<<<<<<< HEAD

				<div class="flex items-center gap-2">
					<!-- XP -->
					<div
						class="flex items-center gap-2 rounded-lg bg-surface-blue-2 px-3 py-2"
					>
						<span class="text-base">⚡</span>

						<div class="flex flex-col leading-tight">
							<span class="text-xs text-ink-gray-6">
								{{ __('XP') }}
							</span>

							<span class="text-sm font-semibold text-ink-gray-9">
								{{ xpValue }}
							</span>
						</div>
					</div>

					<!-- Streak -->
					<button
=======
				<div>
					<button
						v-if="!isAdmin"
>>>>>>> origin/feat/Billing
						type="button"
						@click="showStreakModal = true"
						:aria-label="
							__('View learning streak: {0} days').format(
								streakInfo.data?.current_streak || 0
							)
						"
<<<<<<< HEAD
						class="flex items-center gap-2 rounded-lg bg-surface-amber-2 px-3 py-2 cursor-pointer"
					>
						<span>🔥</span>

						<div class="flex flex-col items-start leading-tight">
							<span class="text-xs text-ink-gray-6">
								{{ __('Streak') }}
							</span>

							<span class="text-sm font-semibold text-ink-gray-9">
								{{ streakInfo.data?.current_streak || 0 }}
								{{ __('days') }}
							</span>
						</div>
=======
						class="bg-surface-amber-2 px-2 py-1 rounded-md cursor-pointer"
					>
						<span> 🔥 </span>
						<span class="text-ink-gray-9">
							{{ streakInfo.data?.current_streak }}
						</span>
>>>>>>> origin/feat/Billing
					</button>
				</div>
			</div>

			<div class="text-lg text-ink-gray-6 leading-6">
				{{ subtitle }}
			</div>
		</div>

		<div
			v-if="isHomeLoading"
			class="flex flex-1 items-center justify-center py-20"
		>
			<LoadingIndicator class="size-5 text-ink-gray-5" />
		</div>
<<<<<<< HEAD

=======
>>>>>>> origin/feat/Billing
		<AdminHome
			v-else-if="isAdmin && currentTab === 'instructor'"
			:liveClasses="adminLiveClasses"
			:evals="adminEvals"
		/>
<<<<<<< HEAD

=======
>>>>>>> origin/feat/Billing
		<StudentHome
			v-else-if="currentTab === 'student'"
			:myLiveClasses="myLiveClasses"
		/>
	</div>
<<<<<<< HEAD

	<Streak v-model="showStreakModal" :streakInfo="streakInfo" />
</template>

<script setup lang="ts">
import { computed, inject, onMounted, ref } from 'vue'
import {
	call,
	createResource,
	LoadingIndicator,
	usePageMeta,
} from 'frappe-ui'
=======
	<Streak v-model="showStreakModal" :streakInfo="streakInfo" />
</template>
<script setup lang="ts">
import { computed, inject, onMounted, ref } from 'vue'
import { call, createResource, LoadingIndicator, usePageMeta } from 'frappe-ui'
>>>>>>> origin/feat/Billing
import { sessionStore } from '@/stores/session'
import StudentHome from '@/pages/Home/StudentHome.vue'
import AdminHome from '@/pages/Home/AdminHome.vue'
import Streak from '@/pages/Home/Streak.vue'

const user = inject<any>('$user')
const { brand } = sessionStore()
<<<<<<< HEAD

const evalCount = ref(0)
const currentTab = ref<'student' | 'instructor'>('student')
const showStreakModal = ref(false)
const xpValue = ref(0)
=======
const evalCount = ref(0)
const currentTab = ref<'student' | 'instructor'>('student')
const showStreakModal = ref(false)
>>>>>>> origin/feat/Billing

const fetchEvalCount = () => {
	call('frappe.client.get_count', {
		doctype: 'LMS Certificate Request',
		filters: {
			member: user?.data?.name,
			status: 'Upcoming',
			date: ['>=', inject<any>('$dayjs')().format('YYYY-MM-DD')],
		},
	}).then((data: any) => {
		evalCount.value = data
	})
}

<<<<<<< HEAD
const fetchXP = () => {
	call('dsa.xp.get_my_xp')
		.then((data: any) => {
			xpValue.value = data || 0
		})
		.catch((error: any) => {
			console.error('XP error:', error)
			xpValue.value = 0
		})
}

=======
>>>>>>> origin/feat/Billing
const isAdmin = computed(() => {
	return (
		user.data?.is_moderator ||
		user.data?.is_instructor ||
		user.data?.is_evaluator
	)
})

const isHomeLoading = computed(() => {
	if (isAdmin.value) {
		return (
			(adminLiveClasses.loading && !adminLiveClasses.data) ||
			(adminEvals.loading && !adminEvals.data)
		)
	}
<<<<<<< HEAD

=======
>>>>>>> origin/feat/Billing
	return myLiveClasses.loading && !myLiveClasses.data
})

onMounted(() => {
	if (isAdmin.value) {
		currentTab.value = 'instructor'
	} else {
		currentTab.value = 'student'
		fetchEvalCount()
<<<<<<< HEAD
		
	}
	fetchXP()
=======
	}
>>>>>>> origin/feat/Billing
})

const myLiveClasses = createResource({
	url: 'lms.lms.api.get_my_live_classes',
<<<<<<< HEAD
	auto: !isAdmin.value,
=======
	auto: !isAdmin.value ? true : false,
>>>>>>> origin/feat/Billing
})

const adminLiveClasses = createResource({
	url: 'lms.lms.api.get_admin_live_classes',
<<<<<<< HEAD
	auto: isAdmin.value,
=======
	auto: isAdmin.value ? true : false,
>>>>>>> origin/feat/Billing
})

const adminEvals = createResource({
	url: 'lms.lms.api.get_admin_evals',
<<<<<<< HEAD
	auto: isAdmin.value,
=======
	auto: isAdmin.value ? true : false,
>>>>>>> origin/feat/Billing
})

const streakInfo = createResource({
	url: 'lms.lms.api.get_streak_info',
	auto: true,
})

const subtitle = computed(() => {
	if (isAdmin.value) {
		let liveClassSuffix =
<<<<<<< HEAD
			adminLiveClasses.data?.length > 1
				? __('live classes')
				: __('live class')

		let evalSuffix =
			adminEvals.data?.length > 1
				? __('evaluations')
				: __('evaluation')

		if (
			adminLiveClasses.data?.length > 0 &&
			adminEvals.data?.length > 0
		) {
=======
			adminLiveClasses.data?.length > 1 ? __('live classes') : __('live class')
		let evalSuffix =
			adminEvals.data?.length > 1 ? __('evaluations') : __('evaluation')
		if (adminLiveClasses.data?.length > 0 && adminEvals.data?.length > 0) {
>>>>>>> origin/feat/Billing
			return __('You have {0} upcoming {1} and {2} {3} scheduled.').format(
				adminLiveClasses.data.length,
				liveClassSuffix,
				adminEvals.data.length,
				evalSuffix
			)
		} else if (adminLiveClasses.data?.length > 0) {
			return __('You have {0} upcoming {1}.').format(
				adminLiveClasses.data.length,
				liveClassSuffix
			)
		} else if (adminEvals.data?.length > 0) {
			return __('You have {0} {1} scheduled.').format(
				adminEvals.data.length,
				evalSuffix
			)
		}
<<<<<<< HEAD

		return __('Manage your courses and batches at a glance')
	} else {
		let liveClassSuffix =
			myLiveClasses.data?.length > 1
				? __('live classes')
				: __('live class')

		let evalSuffix =
			evalCount.value > 1
				? __('evaluations')
				: __('evaluation')

		if (
			myLiveClasses.data?.length > 0 &&
			evalCount.value > 0
		) {
=======
		return __('Manage your courses and batches at a glance')
	} else {
		let liveClassSuffix =
			myLiveClasses.data?.length > 1 ? __('live classes') : __('live class')
		let evalSuffix = evalCount.value > 1 ? __('evaluations') : __('evaluation')
		if (myLiveClasses.data?.length > 0 && evalCount.value > 0) {
>>>>>>> origin/feat/Billing
			return __('You have {0} upcoming {1} and {2} {3} scheduled.').format(
				myLiveClasses.data.length,
				liveClassSuffix,
				evalCount.value,
				evalSuffix
			)
		} else if (myLiveClasses.data?.length > 0) {
			return __('You have {0} upcoming {1}.').format(
				myLiveClasses.data.length,
				liveClassSuffix
			)
		} else if (evalCount.value > 0) {
			return __('You have {0} {1} scheduled.').format(
				evalCount.value,
				evalSuffix
			)
		}
<<<<<<< HEAD

=======
>>>>>>> origin/feat/Billing
		return __('Resume where you left off')
	}
})

usePageMeta(() => {
	return {
		title: __('Home'),
		icon: brand.favicon,
	}
})
<<<<<<< HEAD
</script>
=======
</script>
>>>>>>> origin/feat/Billing
