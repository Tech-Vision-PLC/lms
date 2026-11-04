<template>
	<Dialog v-model:open="show" size="2xl" bare>
		<template #default>
			<Dialog.Title as-child>
				<h2 class="sr-only">{{ __('Command palette') }}</h2>
			</Dialog.Title>
<<<<<<< HEAD
			<div class="text-base" @keydown="onKeydown">
=======
			<div class="text-base">
>>>>>>> origin/feat/Billing
				<div class="flex items-center gap-x-2 ps-4.5 border-b">
					<span class="lucide-search size-4 text-ink-gray-4" />
					<input
						ref="inputRef"
						type="text"
<<<<<<< HEAD
						role="combobox"
						aria-expanded="true"
						aria-controls="command-palette-results"
=======
>>>>>>> origin/feat/Billing
						:placeholder="__('Search')"
						class="w-full border-none bg-transparent py-3 !ps-2 pe-4.5 text-base text-ink-gray-7 placeholder-ink-gray-4 focus:ring-0"
						@input="onInput"
						v-model="query"
						autocomplete="off"
					/>
				</div>

<<<<<<< HEAD
				<div
					id="command-palette-results"
					class="max-h-96 overflow-auto mb-2"
					ref="resultsRef"
				>
					<div class="mt-5 space-y-5">
						<CommandPaletteGroup :list="groups" @select="run" />
					</div>
					<p
						v-if="showsErrorState"
						class="px-4.5 py-2 text-ink-gray-5"
						role="status"
					>
						{{ __('Could not search just now. Try again.') }}
					</p>
					<p
						v-if="showsEmptyState"
						class="px-4.5 py-2 text-ink-gray-5"
						role="status"
					>
						{{ __('No results found') }}
					</p>
=======
				<div class="max-h-96 overflow-auto mb-2">
					<div v-if="query.length" class="mt-5 space-y-5">
						<CommandPaletteGroup
							:list="searchResults"
							@navigateTo="navigateTo"
						/>
					</div>

					<div v-else class="mt-5 space-y-5">
						<CommandPaletteGroup
							:list="jumpToOptions"
							@navigateTo="navigateTo"
						/>
					</div>
>>>>>>> origin/feat/Billing
				</div>

				<div
					class="flex items-center gap-x-5 w-full border-t py-2 text-sm text-ink-gray-7 px-4.5"
				>
					<div class="flex items-center gap-x-2">
						<span :class="chipClass">
							<span class="lucide-move-up size-3.5 text-ink-gray-7" />
						</span>
						<span :class="chipClass">
							<span class="lucide-move-down size-3.5 text-ink-gray-7" />
						</span>
						<span>
							{{ __('to navigate') }}
						</span>
					</div>
					<div class="flex items-center gap-x-2">
						<span :class="chipClass">
							<span class="lucide-corner-down-left size-3.5 text-ink-gray-7" />
						</span>
						<span>
							{{ __('to select') }}
						</span>
					</div>
					<div class="flex items-center gap-x-2">
<<<<<<< HEAD
						<span :class="[wideChipClass, 'text-xs text-ink-gray-7']">
=======
						<span :class="[chipClass, 'px-1.5 text-xs text-ink-gray-7']">
>>>>>>> origin/feat/Billing
							{{ __('esc') }}
						</span>
						<span>
							{{ __('to close') }}
						</span>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import { createResource, debounce, Dialog } from 'frappe-ui'
<<<<<<< HEAD
import { computed, nextTick, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { usersStore } from '@/stores/user'
import { useSettings } from '@/stores/settings'
// @ts-expect-error utils/index.js has no type declarations yet
import { getSidebarLinks } from '@/utils'
import CommandPaletteGroup from './CommandPaletteGroup.vue'
import type { PaletteGroup, PaletteItem, PaletteRoute } from './paletteTypes'
import { MODAL_FORM_ROUTES, routeForSearchHit } from './paletteTypes'
import {
	categoryById,
	visibleCategories,
	visibleNavTargets,
} from './categories'
import { openFormRoute } from '@/composables/useFormRoute'
=======
import { nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { BookOpen, Briefcase, Users } from 'lucide-vue-next'
import CommandPaletteGroup from './CommandPaletteGroup.vue'
>>>>>>> origin/feat/Billing

const chipClass =
	'inline-flex size-5 shrink-0 items-center justify-center rounded-sm bg-surface-gray-2'

<<<<<<< HEAD
// `size-5` fixes a square, which crops a multi-letter key. Width grows instead.
const wideChipClass =
	'inline-flex h-5 min-w-5 w-auto shrink-0 items-center justify-center rounded-sm bg-surface-gray-2 px-1.5'

// Below this the palette keeps showing the jump-to list. The results pane used
// to take over at one character while the search only ran from three, so the
// dialog went blank for exactly the two keystrokes that start every search.
const MIN_QUERY_LENGTH = 2

const show = defineModel<boolean>({ required: true, default: false })
const router = useRouter()
const { userResource } = usersStore()
const settingsStore = useSettings()

// The category the search is narrowed to, or null at the root.
const scope = ref<string | null>(null)
const query = ref<string>('')
const searchResults = ref<PaletteGroup[]>([])
const inputRef = ref<HTMLInputElement | null>(null)
const resultsRef = ref<HTMLElement | null>(null)

// -1 is "the user has not arrowed yet", which is what lets the first ArrowDown
// land on the first row rather than the second.
const activeIndex = ref(-1)

// One token per request. Comparing against the current query instead would miss
// two requests for *different* queries overlapping and landing out of order:
// frappe-ui never aborts the one already in flight. Everything that invalidates
// the search in progress — a scope change, a close, unmounting — bumps this, so
// a response already on its way lands in a scope that no longer wants it and is
// dropped.
let searchToken = 0

// The token the waiting debounced tick is holding. frappe-ui's `debounce` hands
// back a bare function with no `.cancel()`, so a scheduled search is disarmed
// rather than cleared: the tick still runs, sees that `searchToken` has moved
// past it, and asks the server for nothing.
let armedToken = 0
const invalidateSearch = () => {
	searchToken += 1
}

const searchFailed = ref(false)

// The query `searchResults` answers, which is not always the one on screen.
const resultsQuery = ref<string | null>(null)

// Whether a search for the current typing run has come back at all. Tying the
// empty message to `search.loading` instead made it blink off and on with every
// keystroke — the results area collapsed to nothing and the dialog resized on
// each letter, which read as the palette tearing itself apart.
const hasSettled = ref(false)

const search = createResource({ url: 'lms.command_palette.search_sqlite' })

// `getSidebarLinks()` is the list before the site's own on/off flags are applied
// — AppSidebar filters it a second time against these — so a site with Jobs
// switched off was still offered a Jobs row here.
const sidebarVisibility = computed(() => settingsStore.sidebarSettings.data)

const runSearch = async (token: number) => {
	// What this request is for. The response is matched back against it so the
	// rows can say whether they still answer what is in the box.
	const asked = query.value
	const params = scope.value
		? { query: query.value, category: scope.value }
		: { query: query.value }
	try {
		const data = await search.submit(params)
		if (token !== searchToken) return
		searchResults.value = toGroups(data)
		resultsQuery.value = asked
		searchFailed.value = false
		hasSettled.value = true
	} catch (error) {
		if (token !== searchToken) return
		searchResults.value = []
		resultsQuery.value = asked
		searchFailed.value = true
		hasSettled.value = true
	}
}

const isSearching = computed(() => query.value.length >= MIN_QUERY_LENGTH)

/**
 * The rows on screen answer a query the user has already replaced. Going from
 * one valid query to another leaves `isSearching` true, so the query watcher
 * never clears them — deliberately, because clearing per keystroke is the blink
 * that "stop the empty state blinking" fixed. They stay visible and stop being
 * selectable instead, so Enter cannot open a row the query no longer matches.
 */
const resultsAreStale = computed(
	() =>
		isSearching.value &&
		resultsQuery.value !== null &&
		resultsQuery.value !== query.value
)

/** The same test Programs.vue gates its own card click on. */
const routeContext = computed(() => ({
	canEditPrograms:
		!window.read_only_mode &&
		Boolean(
			userResource.data?.is_moderator || userResource.data?.is_instructor
		),
}))

/**
 * Every row the palette offers by name, in the form it takes while searching: a
 * category resolves to its own list page here rather than drilling in, because
 * typing "cour" means "take me to Courses". Account rows belong here too —
 * Settings lived only in the pre-search list, so typing its name emptied the
 * palette and reported that nothing matched.
 */
const searchableSections = computed<PaletteItem[]>(() => {
	const links = getSidebarLinks()
	return [
		...visibleCategories(links, sidebarVisibility.value).map((entry) => ({
			title: __(entry.label),
			icon: entry.icon,
			route: { name: entry.listRoute },
		})),
		...visibleNavTargets(links, sidebarVisibility.value).map((entry) => ({
			title: __(entry.label),
			icon: entry.icon,
			route: { name: entry.route },
		})),
		...accountItems.value,
	]
})

/** Sections whose name the query is starting to spell. */
const matchingSections = computed<PaletteItem[]>(() => {
	const term = query.value.trim().toLowerCase()
	if (!term || scope.value) return []
	return searchableSections.value.filter((section) =>
		String(section.title).toLowerCase().startsWith(term)
	)
})

const groups = computed<PaletteGroup[]>(() => {
	const searched = isSearching.value
	const sections = matchingSections.value
	const stale = resultsAreStale.value
	const hits = searchResults.value.map((group) => ({
		...group,
		isStale: stale,
	}))
	const source = searched
		? sections.length
			? [{ title: __('Jump to'), items: sections }, ...hits]
			: hits
		: browseGroups.value
	// Stale rows are skipped by the counter, not just excluded from it, so the
	// active index keeps addressing the same live row either way.
	let index = 0
	return source.map((group) => ({
		title: group.title,
		items: group.items.map((item) =>
			group.isStale
				? { ...item, isStale: true, isActive: false }
				: { ...item, isActive: index++ === activeIndex.value }
		),
	}))
})

/**
 * Everything drawn, stale rows included. "No results found" answers what is on
 * screen rather than what can be selected — keying it to the selectable rows
 * would blank it for every in-flight keystroke once a stale set was excluded,
 * which is the blink "stop the empty state blinking" fixed.
 */
const renderedCount = computed(() =>
	groups.value.reduce((total, group) => total + group.items.length, 0)
)

/** What the keyboard can reach: a stale row is on screen but not in here. */
const flatItems = computed<PaletteItem[]>(() =>
	groups.value.flatMap((group) => group.items).filter((item) => !item.isStale)
)

const showsEmptyState = computed(
	() =>
		isSearching.value &&
		!renderedCount.value &&
		hasSettled.value &&
		!searchFailed.value
)

/** A failed request is not an empty result set, and saying so hides an outage.
 * Not gated on an empty list either: a query that spells a section name fills
 * one row from `matchingSections`, which is enough to have hidden the failure. */
const showsErrorState = computed(
	() => isSearching.value && searchFailed.value && hasSettled.value
)

const debouncedSearch = debounce(() => {
	if (armedToken !== searchToken) return
	if (isSearching.value) runSearch(armedToken)
}, 300)

const onInput = () => {
	armedToken = ++searchToken
	debouncedSearch()
}

// A trailing tick used to fire its request after the dialog was gone. The token
// dropped the response, but the round trip still went out.
onUnmounted(invalidateSearch)

/** Search hits whose doctype has no route are dropped, not pointed at a wrong page. */
const toGroups = (data: unknown): PaletteGroup[] => {
	if (!Array.isArray(data)) return []
	return data
		.map((group: any) => ({
			title: group.title,
			items: (group.items ?? [])
				.map((item: any) => {
					const route = routeForSearchHit(
						item.doctype,
						item.name,
						routeContext.value
					)
					return route ? { ...item, route } : null
				})
				.filter(Boolean) as PaletteItem[],
		}))
		.filter((group) => group.items.length > 0)
}

watch(query, () => {
	activeIndex.value = -1
	if (!isSearching.value) {
		invalidateSearch()
		searchResults.value = []
		hasSettled.value = false
		searchFailed.value = false
	}
})

watch(show, () => {
	if (show.value) {
		// The palette reads these flags itself rather than trusting AppSidebar to
		// have fetched them; the store hands back the one in-flight request.
		settingsStore.loadSidebarSettings()
		return
	}
	// Without this the palette reopened still narrowed to whatever category was
	// last opened, with no visible sign that it was filtering.
	scope.value = null
	resetSearch()
})

const onKeydown = (e: KeyboardEvent) => {
	if (e.key === 'ArrowDown') {
		e.preventDefault()
		moveActive(1)
	} else if (e.key === 'ArrowUp') {
		e.preventDefault()
		moveActive(-1)
	} else if (e.key === 'Enter') {
		// A result button the user tabbed to takes Enter as a click of its own.
		// Handling it here would open whichever row is highlighted instead.
		if (isResultButton(e.target)) return
		e.preventDefault()
		// Enter with nothing arrowed to opens the top hit, which is what the
		// caret sitting in a search box implies.
		const item = flatItems.value[Math.max(activeIndex.value, 0)]
		if (item) run(item)
	} else if (e.key === 'Escape') {
		if (scope.value) {
			// The dialog closes on Escape at the document level unless this is
			// stopped, which made backing out one level impossible.
			e.preventDefault()
			e.stopPropagation()
			leaveScope()
		} else show.value = false
	} else if (e.key === 'Backspace' && !query.value && scope.value) {
		// Only on an empty query, so Backspace stays an ordinary edit while there
		// is still something to delete.
		e.preventDefault()
		leaveScope()
	}
}

const isResultButton = (target: EventTarget | null): boolean =>
	target instanceof Element && Boolean(target.closest('[data-palette-item]'))

const moveActive = (direction: number) => {
	const total = flatItems.value.length
	if (!total) return
	// The highlight belongs to the input's caret. Arrowing from a result button
	// the user had tabbed to would otherwise leave focus and highlight on
	// different rows, and Enter opens the focused one.
	focusInput()
	const next = activeIndex.value + direction
	if (next < 0) activeIndex.value = total - 1
	else if (next >= total) activeIndex.value = 0
	else activeIndex.value = next
=======
const show = defineModel<boolean>({ required: true, default: false })
const router = useRouter()
const query = ref<string>('')
const searchResults = ref<Array<any>>([])

const search = createResource({
	url: 'lms.command_palette.search_sqlite',
	makeParams: () => ({
		query: query.value,
	}),
	onSuccess() {
		generateSearchResults()
	},
})

const debouncedSearch = debounce(() => {
	if (query.value.length > 2) {
		search.reload()
	}
}, 500)

const onInput = () => {
	debouncedSearch()
}

const generateSearchResults = () => {
	search.data?.forEach((type: any) => {
		let result: { title: string; items: any[] } = { title: '', items: [] }
		result.title = type.title
		type.items.forEach((item: any) => {
			let paramName = item.doctype === 'LMS Course' ? 'courseName' : 'batchName'
			item.route = {
				name: item.doctype === 'LMS Course' ? 'CourseDetail' : 'BatchDetail',
				params: {
					[paramName]: item.name,
				},
			}
			item.isActive = false
		})
		result.items = type.items
		searchResults.value.push(result)
	})
}

watch(query, () => {
	searchResults.value = []
})

watch(show, () => {
	if (!show.value) {
		query.value = ''
		searchResults.value = []
	}
})

onMounted(() => {
	addKeyboardShortcuts()
})

const addKeyboardShortcuts = () => {
	window.addEventListener('keydown', (e: KeyboardEvent) => {
		if (e.key === 'ArrowUp' && show.value) {
			e.preventDefault()
			shortcutForArrowKey(-1)
		} else if (e.key === 'ArrowDown' && show.value) {
			shortcutForArrowKey(1)
		} else if (e.key === 'Enter' && show.value) {
			// A focused result button fires its own click; let that be the
			// single navigation instead of racing this handler.
			if ((e.target as HTMLElement)?.closest?.('[data-palette-item]')) return
			shortcutForEnter()
		} else if (e.key === 'Escape' && show.value) {
			show.value = false
		}
	})
}

const shortcutForArrowKey = (direction: number) => {
	let currentList = query.value.length
		? searchResults.value
		: jumpToOptions.value
	let allItems = currentList.flatMap((result: any) => result.items)
	let indexOfActive = allItems.findIndex((option: any) => option.isActive)
	let newIndex = indexOfActive + direction
	if (newIndex < 0) newIndex = allItems.length - 1
	if (newIndex >= allItems.length) newIndex = 0
	allItems[indexOfActive].isActive = false
	allItems[newIndex].isActive = true
>>>>>>> origin/feat/Billing
	nextTick(scrollActiveItemIntoView)
}

const scrollActiveItemIntoView = () => {
<<<<<<< HEAD
	const active = resultsRef.value?.querySelector<HTMLElement>(
		'[data-palette-item][data-active="true"]'
	)
	if (!active) return
	// Scrolling the row alone left its heading clipped above the fold, so arrowing
	// up to the top row of a group hid which group it belonged to.
	const group = active.closest<HTMLElement>('[data-palette-group]')
	const isFirstOfGroup = group?.querySelector('[data-palette-item]') === active
	;(isFirstOfGroup && group ? group : active).scrollIntoView({
		block: 'nearest',
	})
}

const run = (item: PaletteItem) => {
	if (item.isStale) return
	if (item.category) enterScope(item.category)
	else if (item.perform) {
		show.value = false
		item.perform()
	} else if (item.route) navigateTo(item.route)
}

const enterScope = (category: string) => {
	scope.value = category
	resetSearch()
	focusInput()
}

const leaveScope = () => {
	scope.value = null
	resetSearch()
	focusInput()
}

/** Both directions across a scope boundary clear the same state. The token bump
 * is what stops the old scope's reply, which frappe-ui is still fetching, from
 * repopulating the new one. */
const resetSearch = () => {
	invalidateSearch()
	query.value = ''
	searchResults.value = []
	resultsQuery.value = null
	activeIndex.value = -1
	searchFailed.value = false
	hasSettled.value = false
}

/** Clicking a row destroys that button, so without this the caret would be left
 * on nothing. The keys are bound to the dialog panel and keep working either
 * way; typing is what needs the input back. */
const focusInput = () => {
	nextTick(() => inputRef.value?.focus())
}

const navigateTo = (route: PaletteRoute) => {
	show.value = false
	query.value = ''
	searchResults.value = []
	const to = { name: route.name, params: route.params, query: route.query }
	// push, not replace: reaching a course through the palette should still
	// leave the page you came from on the back stack. A form route needs the
	// marker openFormRoute stamps, or closing the modal ejects the user instead
	// of returning them to the list underneath it.
	if (MODAL_FORM_ROUTES.has(route.name)) openFormRoute(router, to)
	else router.push(to)
}

const scopedCategory = computed(() => categoryById(scope.value))

/** What the palette shows before a search: the categories, or, once inside one,
 * the way out to that category's own page. */
const browseGroups = computed<PaletteGroup[]>(() => {
	const category = scopedCategory.value
	if (category) {
		return [
			{
				title: __(category.label),
				items: [
					{
						title: __('View all {0}').format(__(category.label)),
						icon: category.icon,
						route: { name: category.listRoute },
					},
				],
			},
		]
	}

	const links = getSidebarLinks()
	const groups: PaletteGroup[] = [
		{
			title: __('Jump to'),
			items: [
				...visibleCategories(links, sidebarVisibility.value).map((entry) => ({
					title: __(entry.label),
					icon: entry.icon,
					category: entry.id,
				})),
				// No records to narrow to, so these navigate rather than drill in.
				...visibleNavTargets(links, sidebarVisibility.value).map((entry) => ({
					title: __(entry.label),
					icon: entry.icon,
					route: { name: entry.route },
				})),
			],
		},
	]

	const account = accountItems.value
	if (account.length) groups.push({ title: __('Account'), items: account })
	return groups
})

/** Settings is a dialog owned by the desktop sidebar and open to moderators
 * only; on a phone nothing listens to the flag, so the row would do nothing. */
const accountItems = computed<PaletteItem[]>(() => {
	if (!userResource.data?.is_moderator || !settingsStore.isSettingsMounted) {
		return []
	}
	return [
		{
			title: __('Settings'),
			icon: 'lucide-settings',
			perform: () => {
				settingsStore.isSettingsOpen = true
			},
		},
	]
})
=======
	const activeItem = document.querySelector(
		'.hover\\:bg-surface-gray-2.bg-surface-gray-2'
	) as HTMLElement
	if (activeItem) {
		activeItem.scrollIntoView({ block: 'nearest' })
	}
}

const shortcutForEnter = () => {
	let currentList = query.value.length
		? searchResults.value
		: jumpToOptions.value
	let allItems = currentList.flatMap((result: any) => result.items)
	let activeOption = allItems.find((option) => option.isActive)
	if (activeOption) {
		navigateTo(activeOption.route)
	}
}

const navigateTo = (route: {
	name: string
	params?: Record<string, any>
	query?: Record<string, any>
}) => {
	show.value = false
	query.value = ''
	router.replace({ name: route.name, params: route.params, query: route.query })
}

const jumpToOptions = ref([
	{
		title: __('Jump to'),
		items: [
			{
				title: 'Courses',
				icon: BookOpen,
				route: {
					name: 'Courses',
				},
				isActive: true,
			},
			{
				title: 'Batches',
				icon: Users,
				route: {
					name: 'Batches',
				},
				isActive: false,
			},
			{
				title: 'Jobs',
				icon: Briefcase,
				route: {
					name: 'Jobs',
				},
				isActive: false,
			},
		],
	},
])
>>>>>>> origin/feat/Billing
</script>
<style>
mark {
	background-color: theme('colors.amber.100');
	font-weight: 500;
}
</style>
