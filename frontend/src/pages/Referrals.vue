<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { call } from 'frappe-ui'
import { getLmsRoute } from '@/utils/basePath'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const applying = ref(false)
const copying = ref(false)

const referralCode = ref('')
const referralCount = ref(0)
const codeToApply = ref(
	String(route.query.code || '').trim().toUpperCase()
)

const message = ref('')
const errorMessage = ref('')

const referralLink = computed(() => {
	if (!referralCode.value) return ''
	return `${window.location.origin}${getLmsRoute('referrals')}?code=${encodeURIComponent(referralCode.value)}`
})

async function loadReferralData() {
	loading.value = true
	errorMessage.value = ''

	try {
		const result = await call('lms.referral.get_my_referral_data')
		referralCode.value = result.referral_code || ''
		referralCount.value = result.referral_count || 0
	} catch (error) {
		errorMessage.value =
			error.messages?.[0] ||
			error.message ||
			'Could not load your referral information.'
	} finally {
		loading.value = false
	}
}

async function copyReferralLink() {
	if (!referralLink.value) return

	try {
		copying.value = true
		await navigator.clipboard.writeText(referralLink.value)
		message.value = 'Referral link copied.'
		errorMessage.value = ''
	} catch {
		errorMessage.value =
			'Could not copy automatically. Select and copy the referral link manually.'
	} finally {
		copying.value = false
	}
}

async function applyCode() {
	message.value = ''
	errorMessage.value = ''

	const code = codeToApply.value.trim().toUpperCase()

	if (!code) {
		errorMessage.value = 'Enter a referral code first.'
		return
	}

	applying.value = true

	try {
		const result = await call('lms.referral.apply_referral_code', {
			code,
		})

		message.value = result.message || 'Referral code applied successfully.'
		codeToApply.value = ''
		await loadReferralData()

		if (route.query.code) {
			router.replace({ name: 'Referrals' })
		}
	} catch (error) {
		errorMessage.value =
			error.messages?.[0] ||
			error.message ||
			'Could not apply this referral code.'
	} finally {
		applying.value = false
	}
}

onMounted(loadReferralData)
</script>

<template>
	<div class="mx-auto w-full max-w-3xl px-4 py-8 sm:px-6">
		<div class="mb-8">
			<h1 class="text-2xl font-semibold text-gray-900">
				Referrals
			</h1>
			<p class="mt-2 text-sm text-gray-600">
				Invite people to the platform using your personal referral link.
			</p>
		</div>

		<div
			v-if="loading"
			class="rounded-xl border border-gray-200 p-6 text-sm text-gray-600"
		>
			Loading your referral information...
		</div>

		<template v-else>
			<div
				v-if="errorMessage"
				class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700"
				role="alert"
			>
				{{ errorMessage }}
			</div>

			<div
				v-if="message"
				class="mb-4 rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-700"
				role="status"
			>
				{{ message }}
			</div>

			<section class="rounded-xl border border-gray-200 p-6">
				<h2 class="text-lg font-medium text-gray-900">
					Your referral link
				</h2>
				<p class="mt-1 text-sm text-gray-600">
					Share this link with someone you want to invite.
				</p>

				<div class="mt-4">
					<label
						for="referral-link"
						class="mb-2 block text-sm font-medium text-gray-700"
					>
						Personal link
					</label>
					<div class="flex flex-col gap-2 sm:flex-row">
						<input
							id="referral-link"
							:value="referralLink"
							readonly
							class="min-w-0 flex-1 rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-800"
						/>
						<button
							type="button"
							:disabled="copying || !referralLink"
							class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
							@click="copyReferralLink"
						>
							{{ copying ? 'Copying...' : 'Copy link' }}
						</button>
					</div>
				</div>

				<div class="mt-5">
					<p class="text-sm text-gray-600">Your referral code</p>
					<p class="mt-1 text-xl font-semibold tracking-wide text-gray-900">
						{{ referralCode || 'Unavailable' }}
					</p>
				</div>
			</section>

			<section class="mt-5 rounded-xl border border-gray-200 p-6">
				<h2 class="text-lg font-medium text-gray-900">
					Your referrals
				</h2>
				<p class="mt-2 text-3xl font-semibold text-gray-900">
					{{ referralCount }}
				</p>
				<p class="mt-1 text-sm text-gray-600">
					Users attributed to your referral code.
				</p>
			</section>

			<section class="mt-5 rounded-xl border border-gray-200 p-6">
				<h2 class="text-lg font-medium text-gray-900">
					Apply a referral code
				</h2>
				<p class="mt-1 text-sm text-gray-600">
					If someone invited you, enter their code below. Applying a code
					records the referral; opening a link alone does not.
				</p>

				<form class="mt-4" @submit.prevent="applyCode">
					<label
						for="referral-code"
						class="mb-2 block text-sm font-medium text-gray-700"
					>
						Referral code
					</label>

					<div class="flex flex-col gap-2 sm:flex-row">
						<input
							id="referral-code"
							v-model="codeToApply"
							autocomplete="off"
							placeholder="e.g. REF-AB12CD34"
							class="min-w-0 flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900"
						/>
						<button
							type="submit"
							:disabled="applying"
							class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
						>
							{{ applying ? 'Applying...' : 'Apply code' }}
						</button>
					</div>
				</form>
			</section>
		</template>
	</div>
</template>
