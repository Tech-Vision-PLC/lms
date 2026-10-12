<template>
	<div class="cp-root">
		<div class="cp-page-title">{{ __("CODING PROBLEM") }}</div>

		<div class="coding-problem">
			<header class="cp-header">
				<div class="cp-heading">
					<span class="cp-glyph" aria-hidden="true">&lt;/&gt;</span>
					<div class="cp-title" role="heading" aria-level="3">
						{{ problem?.title || __("Coding Problem") }}
					</div>
				</div>

				<div v-if="problem" class="cp-badges">
					<span
						v-if="problem.difficulty"
						class="cp-badge cp-difficulty"
						:class="difficultyClass"
					>
						{{ problem.difficulty }}
					</span>
					<span v-if="problem.xp_reward > 0" class="cp-badge cp-badge-xp">
						{{ problem.xp_reward }} XP
					</span>
					<span v-if="problem.solved" class="cp-badge cp-badge-solved">
						✓ {{ __("Solved") }}
					</span>
					<button
						type="button"
						class="cp-link-btn"
						:aria-expanded="!problemCollapsed"
						@click="problemCollapsed = !problemCollapsed"
					>
						{{ problemCollapsed ? __("Show problem") : __("Hide problem") }}
						<svg
							class="cp-chevron"
							:class="{ 'is-open': !problemCollapsed }"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
							aria-hidden="true"
						>
							<path d="m6 9 6 6 6-6" />
						</svg>
					</button>
				</div>
			</header>

			<div v-if="loading" class="cp-skeleton" aria-busy="true">
				<span style="width: 38%"></span>
				<span style="width: 92%"></span>
				<span style="width: 84%"></span>
				<span style="width: 60%"></span>
			</div>

			<div v-else-if="loadError" class="cp-load-error" role="alert">
				<span>{{ loadError }}</span>
				<button type="button" class="cp-btn cp-run" @click="loadProblem">
					{{ __("Retry") }}
				</button>
			</div>

			<template v-else-if="problem">
				<div v-show="!problemCollapsed" class="cp-problem">
					<div v-if="hasFacts" class="cp-facts">
						<span
							v-for="topic in problem.topics || []"
							:key="topic"
							class="cp-chip cp-chip-topic"
						>
							{{ topic }}
						</span>
						
					</div>

					<section
						v-for="section in sections"
						:key="section.key"
						class="cp-section"
					>
						<button
							type="button"
							class="cp-section-toggle"
							:aria-expanded="openSections[section.key]"
							@click="openSections[section.key] = !openSections[section.key]"
						>
							<svg
								class="cp-chevron"
								:class="{ 'is-open': openSections[section.key] }"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
								aria-hidden="true"
							>
								<path d="m9 6 6 6-6 6" />
							</svg>
							{{ section.label }}
						</button>

						<div
							v-show="openSections[section.key]"
							class="cp-rich"
							v-html="section.html"
						></div>
					</section>
				</div>

				<div class="cp-workspace">
					<section class="cp-card" :aria-label="__('Code editor')">
						<div class="cp-toolbar">
							<div class="cp-toolbar-group">
								<label class="cp-lang">
									<span class="cp-sr-only">{{ __("Programming language") }}</span>
									<select
										v-model.number="languageId"
										:disabled="busy"
										@change="changeLanguage"
									>
										<option
											v-for="language in languages"
											:key="language.id"
											:value="language.id"
										>
											{{ language.label }}
										</option>
									</select>
									<svg
										class="cp-lang-chevron"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
										aria-hidden="true"
									>
										<path d="m6 9 6 6 6-6" />
									</svg>
								</label>

								<button
									type="button"
									class="cp-icon-btn"
									:disabled="busy"
									:title="__('Reset to starter code')"
									:aria-label="__('Reset to starter code')"
									@click="resetCode"
								>
									<svg
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
										aria-hidden="true"
									>
										<path d="M3 12a9 9 0 1 0 3-6.7" />
										<path d="M3 4v5h5" />
									</svg>
								</button>
							</div>

							<div class="cp-toolbar-group">
								<button
									type="button"
									class="cp-btn cp-run"
									:disabled="busy"
									:aria-busy="running"
									@click="runCode"
								>
									<span v-if="busy" class="cp-spinner" aria-hidden="true"></span>
									<svg
										v-else
										class="cp-btn-icon"
										viewBox="0 0 24 24"
										fill="currentColor"
										aria-hidden="true"
									>
										<path d="M7 4.5v15l13-7.5-13-7.5z" />
									</svg>
									{{ __("Run") }}
								</button>

								<button
									type="button"
									class="cp-btn cp-submit"
									:disabled="busy"
									:aria-busy="submitting"
									@click="submitCode"
								>
									<span v-if="busy" class="cp-spinner" aria-hidden="true"></span>
									<svg
										v-else
										class="cp-btn-icon"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2.5"
										stroke-linecap="round"
										stroke-linejoin="round"
										aria-hidden="true"
									>
										<polyline points="20 6 9 17 4 12" />
									</svg>
									{{ __("Submit") }}
								</button>
							</div>
						</div>

						<div class="cp-editor-area">
							<MonacoEditor
								ref="monacoEditor"
								v-model="code"
								:language="currentLanguage"
							/>
						</div>
					</section>

					<section class="cp-card cp-terminal" :aria-label="__('Terminal')">
						<div class="cp-terminal-header">
							<div class="cp-result-tabs" role="tablist">
								<button
									type="button"
									role="tab"
									:aria-selected="activeTab === 'solution'"
									:class="{ 'is-active': activeTab === 'solution' }"
									@click="selectSolutionTab"
								>
									<svg
										class="cp-solution-tab-icon"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="1.8"
										stroke-linecap="round"
										stroke-linejoin="round"
										aria-hidden="true"
									>
										<path d="M9 3h6" />
										<path d="M10 3v4l-4.5 8.5A3.5 3.5 0 0 0 8.6 21h6.8a3.5 3.5 0 0 0 3.1-5.5L14 7V3" />
										<path d="M8 14h8" />
										<path d="M9.5 17h5" />
									</svg>
									{{ __("Solution") }}
								</button>

								<button
									type="button"
									role="tab"
									:aria-selected="activeTab === 'testcase'"
									:class="{ 'is-active': activeTab === 'testcase' }"
									@click="activeTab = 'testcase'"
								>
									<span class="cp-green cp-tab-glyph">☑</span>
									{{ __("Testcase") }}
								</button>

								<button
									type="button"
									role="tab"
									:aria-selected="activeTab === 'result'"
									:class="{ 'is-active': activeTab === 'result' }"
									@click="activeTab = 'result'"
								>
									<span class="cp-green cp-tab-glyph">&gt;_</span>
									{{ __("Test Result") }}
								</button>
							</div>

							<button
								v-if="activeTab === 'result' && (outcome || terminalError) && !busy"
								type="button"
								@click="clearResults"
							>
								{{ __("Clear") }}
							</button>
						</div>

						<div class="cp-terminal-body">
							<div v-if="activeTab === 'solution'" class="cp-solution-output">
								<div
									v-if="solutionLoading"
									class="cp-solution-state"
									role="status"
									aria-live="polite"
								>
									<svg
										class="cp-solution-state-icon"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="1.8"
										stroke-linecap="round"
										stroke-linejoin="round"
										aria-hidden="true"
									>
										<path d="M9 3h6" />
										<path d="M10 3v4l-4.5 8.5A3.5 3.5 0 0 0 8.6 21h6.8a3.5 3.5 0 0 0 3.1-5.5L14 7V3" />
										<path d="M8 14h8" />
										<path d="M9.5 17h5" />
									</svg>
									<strong>{{ __("Opening solution…") }}</strong>
									<span>{{ __("Please wait") }}</span>
									<span class="cp-solution-spinner" aria-hidden="true"></span>
								</div>

								<div
									v-else-if="solutionError"
									class="cp-solution-state is-error"
									role="alert"
								>
									<strong>{{ solutionErrorTitle }}</strong>
									<p>{{ solutionError }}</p>
									<button
										v-if="solutionErrorKind !== 'unavailable'"
										type="button"
										class="cp-solution-button"
										@click="retrySolution"
									>
										{{ __("Retry") }}
									</button>
								</div>

								<div
									v-else-if="solutionUnlocked && solutionContent"
									class="cp-solution-viewer"
								>
									<div class="cp-solution-header">
										<div>
											<div class="cp-solution-title">
												<svg
													viewBox="0 0 24 24"
													fill="none"
													stroke="currentColor"
													stroke-width="1.8"
													stroke-linecap="round"
													stroke-linejoin="round"
													aria-hidden="true"
												>
													<path d="M9 3h6" />
													<path d="M10 3v4l-4.5 8.5A3.5 3.5 0 0 0 8.6 21h6.8a3.5 3.5 0 0 0 3.1-5.5L14 7V3" />
													<path d="M8 14h8" />
													<path d="M9.5 17h5" />
												</svg>
												{{ __("Official Solution") }}
											</div>
											<div class="cp-solution-subtitle">
												{{ __("Editorial implementation") }}
											</div>
										</div>

										<span class="cp-solution-language">{{ solutionLanguageLabel }}</span>
									</div>

									<div
										class="cp-solution-code"
										tabindex="0"
										role="region"
										:aria-label="__('Official solution code')"
									><pre><code>{{ solutionContent }}</code></pre></div>
								</div>

								<div v-else class="cp-solution-state">
									<svg
										class="cp-solution-state-icon"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="1.8"
										stroke-linecap="round"
										stroke-linejoin="round"
										aria-hidden="true"
									>
										<path d="M9 3h6" />
										<path d="M10 3v4l-4.5 8.5A3.5 3.5 0 0 0 8.6 21h6.8a3.5 3.5 0 0 0 3.1-5.5L14 7V3" />
										<path d="M8 14h8" />
										<path d="M9.5 17h5" />
									</svg>
									<strong>{{
										solutionFree
											? __("Official Solution")
											: __("Official Solution is locked")
									}}</strong>
									<span v-if="!solutionFree && solutionCost > 0">
										{{ __("Unlock it once for") }} {{ solutionCost }} XP
									</span>
									<span v-else-if="solutionFree && problem.solved && !solutionUnlocked">
										{{ __("Free — you already solved this problem") }}
									</span>
									<button
										type="button"
										class="cp-solution-button is-primary"
										@click="solutionFree ? requestSolution() : openSolutionConfirm()"
									>
										{{ solutionFree ? __("View Solution") : __("Unlock Solution") }}
									</button>
								</div>
							</div>

							<div v-else-if="activeTab === 'testcase'" class="cp-testcase">
								<div class="cp-case-tabs">
									<button
										v-for="(testCase, index) in testCases"
										:key="testCase.key"
										type="button"
										:class="{ 'is-active': activeCaseIndex === index }"
										@click="activeCaseIndex = index"
									>
										{{ __("Case") }} {{ index + 1 }}
									</button>

									<button
										type="button"
										class="cp-add-case"
										:title="__('Add test case')"
										:aria-label="__('Add test case')"
										@click="addTestCase"
									>
										+
									</button>
								</div>

								<label :for="inputId">{{ __("Input") }} =</label>
								<textarea
									:id="inputId"
									v-model="testCases[activeCaseIndex].input"
									spellcheck="false"
									:placeholder="__('Enter input passed to your program…')"
								></textarea>
							</div>

							<template v-else>
								<div v-if="busy" class="cp-muted">
									{{ __("Running…") }}
								</div>

								<div v-else-if="outcome" class="cp-results">
									<div class="cp-result-summary">
										<strong :class="`is-${outcome.tone}`">
											{{ outcome.label }}
										</strong>

										<span v-if="outcome.runtime">
											{{ __("Runtime") }}: {{ outcome.runtime }}
										</span>
										<span v-if="outcome.memory">
											{{ __("Memory") }}: {{ outcome.memory }}
										</span>
									</div>

									<div v-if="xpLine" class="cp-xp-line" :class="`is-${xpLine.tone}`">
										<strong v-if="xpLine.tone === 'awarded'">{{ xpLine.text }}</strong>
										<span v-else>{{ xpLine.text }}</span>
										<span v-if="xpLine.sub">{{ xpLine.sub }}</span>
									</div>

									<div v-if="hasComplexity" class="cp-complexity-info">
										<div
											v-for="row in complexityRows"
											:key="row.label"
											class="cp-complexity-row"
										>
											<label>{{ row.label }}</label>
											<span>
												<span
													class="cp-complexity-value"
													:class="complexityClass(row.result)"
													>{{ row.value || __("Unknown") }}</span
												>
												<span
													class="cp-complexity-result"
													:class="complexityClass(row.result)"
												>
													<span class="cp-complexity-icon" aria-hidden="true">{{
														complexityIcon(row.result)
													}}</span>
													{{ row.result || __("Unknown") }}
												</span>
											</span>
										</div>
									</div>

									<div class="cp-case-tabs cp-result-cases">
										<button
											v-for="(testCase, index) in outcome.cases"
											:key="testCase.index"
											type="button"
											:class="{ 'is-active': activeResultCaseIndex === index }"
											@click="activeResultCaseIndex = index"
										>
											<span
												:class="
													testCase.status === 'Accepted' ? 'cp-case-pass' : 'cp-case-fail'
												"
											>
												■
											</span>
											{{ __("Case") }} {{ testCase.index }}
										</button>
									</div>

									<div v-if="activeCase" class="cp-result-details">
										<label>{{ __("Input") }}</label>
										<pre>{{ activeCase.input || __("No input") }}</pre>

										<template v-if="hasExpected">
											<label>{{ __("Expected Output") }}</label>
											<pre>{{ activeCase.expected_output || __("No output") }}</pre>
										</template>

										<label>{{ activeCaseError ? __("Error") : __("Output") }}</label>
										<pre :class="{ 'is-error': activeCaseError }">{{
											activeCaseError || activeCase.actual_output || __("No output")
										}}</pre>
									</div>
								</div>

								<pre v-else-if="terminalError">{{ terminalError }}</pre>

								<div v-else class="cp-empty-result">
									{{ __("You must run your code first") }}
								</div>
							</template>
						</div>
					</section>
				</div>
			</template>
		</div>

		<Teleport to="body">
			<Transition name="dsa-xp-toast">
				<div
					v-if="xpToast"
					class="dsa-xp-toast"
					role="status"
					aria-live="polite"
					@click="dismissXpToast"
				>
					<span class="dsa-xp-toast-icon" aria-hidden="true">★</span>
					<div class="dsa-xp-toast-body">
						<strong>+{{ xpToast.gained }} XP</strong>
						<span>{{ __("Total XP") }}: {{ xpToast.total }}</span>
					</div>
				</div>
			</Transition>
		</Teleport>

		<Teleport to="body">
			<Transition name="cp-solution-modal-fade">
				<div
					v-if="showSolutionConfirm"
					class="cp-solution-modal-backdrop"
					@click.self="closeSolutionConfirm"
					@keydown.esc="closeSolutionConfirm"
				>
					<div
						class="cp-solution-modal"
						role="dialog"
						aria-modal="true"
						aria-labelledby="cp-solution-modal-title"
					>
						<div class="cp-solution-modal-icon">
							<svg
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="1.8"
								stroke-linecap="round"
								stroke-linejoin="round"
								aria-hidden="true"
							>
								<path d="M9 3h6" />
								<path d="M10 3v4l-4.5 8.5A3.5 3.5 0 0 0 8.6 21h6.8a3.5 3.5 0 0 0 3.1-5.5L14 7V3" />
								<path d="M8 14h8" />
								<path d="M9.5 17h5" />
							</svg>
						</div>

						<h2 id="cp-solution-modal-title">{{ __("Official Solution") }}</h2>

						<p class="cp-solution-modal-lead">
							{{
								solutionCost > 0
									? __("Opening this solution costs")
									: __("Opening this solution is free")
							}}
						</p>

						<div v-if="solutionCost > 0" class="cp-solution-modal-cost">
							{{ solutionCost }}<span>XP</span>
						</div>

						<p v-if="xpLoaded" class="cp-solution-modal-balance">
							{{ __("Your current XP") }}: <strong>{{ xpTotal }}</strong>
						</p>

						<p class="cp-solution-modal-note">
							{{
								solutionCost > 0
									? __("You only pay once for this problem.")
									: __("No XP will be spent. You can reopen it any time.")
							}}
						</p>

						<p v-if="solutionForfeitsXp" class="cp-solution-modal-warning">
							{{ __("Opening the solution before solving this problem means solving it will not award its") }}
							{{ problem?.xp_reward }} XP.
						</p>

						<div
							v-if="solutionInsufficientXp && !solutionError"
							class="cp-solution-modal-error"
							role="alert"
						>
							<strong>{{ __("Not enough XP") }}</strong>
							<span>
								{{ __("You don't have enough XP to open this solution.") }}
								{{ __("You need") }} {{ solutionCost }} XP,
								{{ __("but you only have") }} {{ xpTotal }} XP.
							</span>
						</div>

						<div v-if="solutionError" class="cp-solution-modal-error" role="alert">
							<strong>{{ solutionErrorTitle }}</strong>
							<span>{{ solutionError }}</span>
						</div>

						<div class="cp-solution-modal-actions">
							<button
								ref="solutionCancelButton"
								type="button"
								class="cp-solution-button"
								:disabled="solutionLoading"
								@click="closeSolutionConfirm"
							>
								{{ __("Cancel") }}
							</button>

							<button
								type="button"
								class="cp-solution-button is-primary"
								:disabled="solutionLoading || solutionInsufficientXp"
								@click="confirmSolutionUnlock"
							>
								<span
									v-if="solutionLoading"
									class="cp-solution-spinner is-small"
									aria-hidden="true"
								></span>
								{{ __("Unlock Solution") }}
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>
	</div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import MonacoEditor from "./MonacoEditor.vue";

const props = defineProps({
	problem: {
		type: String,
		required: true,
	},
});

const __ = window.__ || ((text) => text);

const languages = [
	{ id: 71, label: "Python", monaco: "python", starter: "# Write your Python solution here\n" },
	{ id: 54, label: "C++", monaco: "cpp", starter: "// Write your C++ solution here\n" },
	{
		id: 63,
		label: "JavaScript",
		monaco: "javascript",
		starter: "// Write your JavaScript solution here\n",
	},
	{ id: 62, label: "Java", monaco: "java", starter: "// Write your Java solution here\n" },
];

const DEFAULT_LANGUAGE_ID = 71;
const languageId = ref(DEFAULT_LANGUAGE_ID);
let previousLanguageId = DEFAULT_LANGUAGE_ID;

const problem = ref(null);
const loading = ref(true);
const loadError = ref("");

const code = ref("");

const running = ref(false);
const submitting = ref(false);
const busy = computed(() => running.value || submitting.value);

const activeTab = ref("testcase");
const testCases = ref([{ key: 1, input: "" }]);
const activeCaseIndex = ref(0);

const outcome = ref(null);
const terminalError = ref("");
const activeResultCaseIndex = ref(0);

const problemCollapsed = ref(false);
const openSections = reactive({
	description: true,
	examples: true,
	constraints: true,
	hint: false,
});

const monacoEditor = ref(null);

const xpToast = ref(null);
const xpTotal = ref(0);
const xpLoaded = ref(false);

const solutionUnlocked = ref(false);
const solutionLoading = ref(false);
const solutionError = ref("");
const solutionErrorKind = ref("");
const solutionContent = ref("");
const solutionLanguageId = ref(null);
const showSolutionConfirm = ref(false);
const solutionCancelButton = ref(null);
let solutionRequestId = 0;

const XP_TOAST_VISIBLE_MS = 4500;
let xpToastTimer = null;

const inputId = `cp-stdin-${Math.random().toString(36).slice(2, 8)}`;

let generation = 0;
let disposed = false;
let nextTestCaseKey = 2;
let codeDrafts = {};

const currentLanguage = computed(
	() => languages.find((language) => language.id === languageId.value)?.monaco || "cpp"
);

const difficultyClass = computed(() => {
	const value = String(problem.value?.difficulty || "").toLowerCase();
	return ["easy", "medium", "hard"].includes(value) ? `is-${value}` : "";
});

const hasFacts = computed(
	() =>
		Boolean(problem.value?.topics?.length) ||
		Boolean(problem.value?.time_complexity) ||
		Boolean(problem.value?.space_complexity)
);

const sections = computed(() => {
	const data = problem.value;

	if (!data) return [];

	return [
		{ key: "description", label: __("Description"), html: sanitize(data.description) },
		{ key: "examples", label: __("Examples"), html: sanitize(data.examples) },
		{ key: "constraints", label: __("Constraints"), html: sanitize(data.constraints) },
		{ key: "hint", label: __("Hint"), html: sanitize(data.hint) },
	].filter((section) => section.html.trim());
});

const activeCase = computed(() => outcome.value?.cases?.[activeResultCaseIndex.value] || null);

const hasExpected = computed(() => {
	const expected = activeCase.value?.expected_output;
	return expected !== null && expected !== undefined;
});

const activeCaseError = computed(() => {
	const errors = activeCase.value?.errors || [];
	return errors.map((error) => error.text).join("\n");
});

const xpLine = computed(() => {
	const xp = outcome.value?.xp;

	if (!xp) return null;

	if (xp.awarded && Number(xp.gained) > 0) {
		return {
			tone: "awarded",
			text: `+${xp.gained} XP`,
			sub: Number.isFinite(Number(xp.total)) ? `${__("Total XP")}: ${xp.total}` : "",
		};
	}

	if (xp.already_awarded) {
		return { tone: "muted", text: __("Already solved"), sub: "" };
	}

	if (xp.solution_first) {
		return {
			tone: "muted",
			text: __("No XP awarded — the official solution was opened first"),
			sub: "",
		};
	}

	if (xp.error) {
		return { tone: "error", text: xp.error, sub: "" };
	}

	return null;
});

const hasComplexity = computed(() => {
	const complexity = outcome.value?.complexity;
	return Boolean(complexity && (complexity.time || complexity.space));
});

const complexityRows = computed(() => {
	const complexity = outcome.value?.complexity;

	if (!complexity) return [];

	return [
		{ label: __("Time Complexity"), value: complexity.time, result: complexity.timeResult },
		{ label: __("Space Complexity"), value: complexity.space, result: complexity.spaceResult },
	];
});

const solutionCost = computed(() => Math.max(0, Number(problem.value?.solution_xp_deduction) || 0));

const solutionFree = computed(() => solutionUnlocked.value || Boolean(problem.value?.solved));

const solutionInsufficientXp = computed(
	() =>
		xpLoaded.value &&
		!solutionFree.value &&
		solutionCost.value > 0 &&
		xpTotal.value < solutionCost.value
);

const solutionForfeitsXp = computed(
	() => Number(problem.value?.xp_reward) > 0 && !solutionFree.value
);

const solutionLanguageLabel = computed(
	() =>
		languages.find((language) => language.id === solutionLanguageId.value)?.label ||
		languages.find((language) => language.id === languageId.value)?.label ||
		languages[0].label
);

const solutionErrorTitle = computed(() => {
	if (solutionErrorKind.value === "xp") return __("Not enough XP");
	if (solutionErrorKind.value === "unavailable") return __("No solution available");
	return __("Couldn't open the solution");
});

function dismissXpToast() {
	clearTimeout(xpToastTimer);
	xpToastTimer = null;
	xpToast.value = null;
}

function showXpToast(gained, total) {
	clearTimeout(xpToastTimer);
	xpToast.value = { gained, total };
	xpToastTimer = setTimeout(dismissXpToast, XP_TOAST_VISIBLE_MS);
}

function applyXpToast(result) {
	const xp = result?.xp;

	if (!xp) return;

	const total = Number(xp.total);

	if (Number.isFinite(total)) {
		xpTotal.value = total;
		xpLoaded.value = true;
	}

	if (result.status === "Accepted" && xp.awarded && Number(xp.gained) > 0) {
		showXpToast(Number(xp.gained), Number.isFinite(total) ? total : 0);
	}
}

function formatRuntime(runtime) {
	const seconds = Number(runtime);

	if (!Number.isFinite(seconds) || seconds < 0) return "";
	if (seconds === 0) return "0 ms";
	if (seconds < 1) return `${Math.round(seconds * 1000)} ms`;

	return `${seconds.toFixed(2)} s`;
}

function formatMemory(memory) {
	const kb = Number(memory);

	if (!Number.isFinite(kb) || kb < 0) return "";
	if (kb === 0) return "0 KB";
	if (kb < 1024) return `${Math.round(kb)} KB`;

	const mb = kb / 1024;

	if (mb < 1024) return `${mb.toFixed(2)} MB`;

	return `${(mb / 1024).toFixed(2)} GB`;
}

function displayStatus(status) {
	const statusMap = {
		accepted: __("Accepted"),
		"wrong answer": __("Wrong Answer"),
		"time limit exceeded": __("Time Limit Exceeded"),
		"compilation error": __("Compilation Error"),
		"runtime error": __("Runtime Error"),
		failed: __("Wrong Answer"),
		running: __("Running"),
		queued: __("Queued"),
		rejected: __("Rejected"),
	};

	return statusMap[String(status || "").toLowerCase()] || status || __("Finished");
}

function toneFor(label) {
	const value = String(label || "").toLowerCase();

	if (!value) return "neutral";
	if (value === "accepted") return "success";
	if (value === "running" || value === "queued") return "pending";

	return "danger";
}

function classifyError(text) {
	return /\berror:|SyntaxError|cannot find symbol|undefined reference|was not declared|expected .* before/i.test(
		text
	)
		? __("Compilation Error")
		: __("Runtime Error");
}

function complexityClass(result) {
	const value = String(result || "").toLowerCase();

	if (value === "optimal") return "optimal";
	if (value === "too complex") return "too-complex";

	return "unknown";
}

function complexityIcon(result) {
	const value = String(result || "").toLowerCase();

	if (value === "optimal") return "✓";
	if (value === "too complex") return "⚠";

	return "";
}

function complexityRejectionLabel(timeResult, spaceResult) {
	const time = timeResult === "Too Complex";
	const space = spaceResult === "Too Complex";

	if (time && space) return __("Time & Space Complexity Exceeded");
	if (time) return __("Time Complexity Exceeded");
	if (space) return __("Space Complexity Exceeded");

	return null;
}

function sanitize(value) {
	const documentNode = new DOMParser().parseFromString(value || "", "text/html");

	for (const element of documentNode.body.querySelectorAll(
		"script,style,iframe,object,embed,link"
	)) {
		element.remove();
	}

	for (const element of documentNode.body.querySelectorAll("*")) {
		for (const attribute of [...element.attributes]) {
			const name = attribute.name.toLowerCase();

			if (
				name.startsWith("on") ||
				(["href", "src"].includes(name) && /^\s*javascript:/i.test(attribute.value))
			) {
				element.removeAttribute(attribute.name);
			}
		}
	}

	return documentNode.body.innerHTML;
}

function extractMessage(data, fallback) {
	try {
		if (data?._server_messages) {
			const messages = JSON.parse(data._server_messages)
				.map((entry) => {
					try {
						return JSON.parse(entry).message;
					} catch {
						return entry;
					}
				})
				.filter(Boolean)
				.join("\n");

			if (messages) {
				return new DOMParser().parseFromString(messages, "text/html").body.textContent;
			}
		}
	} catch {}

	if (typeof data?.exception === "string" && data.exception) {
		return data.exception.replace(/^[\w.]+:\s*/, "");
	}

	if (typeof data?.message === "string" && data.message) {
		return data.message;
	}

	return fallback;
}

async function dsaApi(method, args = {}, options = {}) {
	const { methodType = "GET" } = options;

	let response;

	if (methodType === "POST") {
		response = await fetch(`/api/method/dsa.api.${method}`, {
			method: "POST",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
				"X-Frappe-CSRF-Token": window.csrf_token || "fetch",
			},
			body: JSON.stringify(args),
		});
	} else {
		const params = new URLSearchParams();

		Object.entries(args).forEach(([key, value]) => {
			if (value !== undefined && value !== null) {
				params.append(key, value);
			}
		});

		response = await fetch(`/api/method/dsa.api.${method}?${params}`, {
			credentials: "include",
		});
	}

	let data = {};

	try {
		data = await response.json();
	} catch {}

	if (!response.ok || data.exc) {
		throw new Error(extractMessage(data, `DSA API request failed: ${method}`));
	}

	return data.message;
}

function wait(milliseconds) {
	return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function starterFor(id) {
	const starters = problem.value?.starter_codes || {};
	const language = languages.find((item) => item.id === id) || languages[0];

	return (
		starters[String(id)] ||
		(id === 54 ? problem.value?.starter_code : "") ||
		language.starter
	);
}

function resetSolutionState() {
	solutionRequestId += 1;
	solutionUnlocked.value = false;
	solutionLoading.value = false;
	solutionError.value = "";
	solutionErrorKind.value = "";
	solutionContent.value = "";
	solutionLanguageId.value = null;
	showSolutionConfirm.value = false;
}

function solutionErrorMessage(err) {
	const message = typeof err?.message === "string" ? err.message.trim() : "";

	if (!message || err instanceof TypeError || /^DSA API request failed/.test(message)) {
		return __("Could not open the solution. Please check your connection and try again.");
	}

	return message;
}

function solutionUnavailableMessage(id) {
	const label = languages.find((language) => language.id === id)?.label || "";
	return `${__("No official solution is available for")} ${label}.`;
}

async function loadXp() {
	try {
		const summary = await dsaApi("get_xp_summary");

		if (disposed) return;

		xpTotal.value = Number(summary?.total_xp) || 0;
		xpLoaded.value = true;
	} catch (err) {
		console.error(err);
	}
}

async function checkSolutionUnlock(problemName) {
	if (!problemName) return;

	try {
		const result = await dsaApi("check_solution_unlock", { problem: problemName });

		if (disposed || problem.value?.name !== problemName) return;

		solutionUnlocked.value = Boolean(result?.unlocked);

		if (
			solutionUnlocked.value &&
			activeTab.value === "solution" &&
			!solutionLoading.value &&
			!solutionContent.value
		) {
			showSolutionConfirm.value = false;
			requestSolution();
		}
	} catch (err) {
		console.error(err);
	}
}

function openSolutionConfirm() {
	solutionError.value = "";
	solutionErrorKind.value = "";
	showSolutionConfirm.value = true;
}

function closeSolutionConfirm() {
	if (solutionLoading.value) return;

	showSolutionConfirm.value = false;
	solutionError.value = "";
	solutionErrorKind.value = "";
}

function confirmSolutionUnlock() {
	if (solutionLoading.value || solutionInsufficientXp.value) return;

	requestSolution();
}

function retrySolution() {
	if (solutionFree.value) {
		requestSolution();
	} else {
		openSolutionConfirm();
	}
}

function selectSolutionTab() {
	activeTab.value = "solution";

	if (solutionLoading.value) return;

	if (!solutionFree.value) {
		openSolutionConfirm();
		return;
	}

	if (solutionContent.value && solutionLanguageId.value === languageId.value) {
		solutionError.value = "";
		solutionErrorKind.value = "";
		return;
	}

	requestSolution();
}

async function requestSolution() {
	if (!problem.value) return;

	const problemName = problem.value.name;
	const requestedLanguageId = languageId.value;
	const requestId = ++solutionRequestId;

	solutionLoading.value = true;
	solutionError.value = "";
	solutionErrorKind.value = "";

	try {
		const result = await dsaApi(
			"open_solution",
			{ problem: problemName, language_id: requestedLanguageId },
			{ methodType: "POST" }
		);

		if (disposed || requestId !== solutionRequestId) return;

		if (!result || typeof result.solution !== "string" || !result.solution.trim()) {
			showSolutionConfirm.value = false;
			solutionErrorKind.value = "unavailable";
			solutionError.value = solutionUnavailableMessage(requestedLanguageId);
			return;
		}

		solutionContent.value = result.solution;
		solutionLanguageId.value = Number(result.language_id) || requestedLanguageId;
		solutionUnlocked.value = true;

		if (result.solved && problem.value) problem.value.solved = true;

		showSolutionConfirm.value = false;
		activeTab.value = "solution";

		const remaining = Number(result.remaining_xp);

		if (
			result.remaining_xp !== null &&
			result.remaining_xp !== undefined &&
			Number.isFinite(remaining)
		) {
			xpTotal.value = remaining;
			xpLoaded.value = true;
		}

		if (languageId.value !== requestedLanguageId) {
			requestSolution();
		}
	} catch (err) {
		if (disposed || requestId !== solutionRequestId) return;

		const message = solutionErrorMessage(err);
		let kind = "error";

		if (/no official solution|unsupported programming language|not supported/i.test(message)) {
			kind = "unavailable";
		} else if (/\bxp\b/i.test(message)) {
			kind = "xp";
		}

		solutionErrorKind.value = kind;

		if (kind === "unavailable") {
			showSolutionConfirm.value = false;
			solutionError.value = solutionUnavailableMessage(requestedLanguageId);
		} else {
			solutionError.value = message;
		}
	} finally {
		if (requestId === solutionRequestId) {
			solutionLoading.value = false;
		}
	}
}

async function loadProblem() {
	loading.value = true;
	loadError.value = "";
	generation += 1;

	try {
		const loaded = await dsaApi("get_problem", { name: props.problem });

		if (disposed) return;

		problem.value = loaded;

		codeDrafts = {};
		languageId.value = DEFAULT_LANGUAGE_ID;
		previousLanguageId = DEFAULT_LANGUAGE_ID;
		code.value = starterFor(DEFAULT_LANGUAGE_ID);

		testCases.value = (loaded.test_cases || []).map((testCase) => ({
			key: nextTestCaseKey++,
			input: testCase.input || "",
		}));

		if (!testCases.value.length) {
			testCases.value = [{ key: nextTestCaseKey++, input: "" }];
		}

		activeCaseIndex.value = 0;
		activeTab.value = "testcase";
		clearResults();

		resetSolutionState();
		checkSolutionUnlock(loaded.name);
		loadXp();
	} catch (err) {
		if (disposed) return;

		console.error(err);
		loadError.value = err.message || __("Failed to load coding problem.");
	} finally {
		if (!disposed) loading.value = false;
	}
}

function changeLanguage() {
	codeDrafts[previousLanguageId] = code.value;

	code.value = codeDrafts[languageId.value] ?? starterFor(languageId.value);

	previousLanguageId = languageId.value;

	clearResults();
}

function resetCode() {
	if (busy.value) return;

	if (
		code.value !== starterFor(languageId.value) &&
		!window.confirm(__("Reset the editor to the starter code? Your changes will be lost."))
	) {
		return;
	}

	code.value = starterFor(languageId.value);
	codeDrafts[languageId.value] = code.value;
}

function addTestCase() {
	testCases.value.push({ key: nextTestCaseKey++, input: "" });
	activeCaseIndex.value = testCases.value.length - 1;
}

function clearResults() {
	outcome.value = null;
	terminalError.value = "";
	activeResultCaseIndex.value = 0;
}

function showError(err) {
	console.error(err);

	outcome.value = null;
	terminalError.value = err?.message || __("Something went wrong.");
}

function buildRunOutcome(queued, result, caseIndex, input) {
	const complexity = {
		time: queued.complexity || "",
		space: queued.space_complexity || "",
		timeResult: queued.complexity_result || "",
		spaceResult: queued.space_complexity_result || "",
	};

	const rejection = complexityRejectionLabel(complexity.timeResult, complexity.spaceResult);
	const label = rejection || displayStatus(result.status);

	const errors = [];

	if (result.compile_output) {
		errors.push({ label: __("Compilation Error"), text: result.compile_output });
	}

	if (result.stderr) {
		errors.push({ label: __("Standard Error"), text: result.stderr });
	}

	if (result.message) {
		errors.push({ label: __("Message"), text: result.message });
	}

	return {
		kind: "run",
		pending: false,
		label,
		tone: rejection ? "danger" : toneFor(label),
		runtime: result.time != null ? formatRuntime(result.time) : "",
		memory: result.memory != null ? formatMemory(result.memory) : "",
		passed: 0,
		total: 0,
		xp: null,
		complexity,
		cases: [
			{
				index: caseIndex + 1,
				status: label,
				input,
				expected_output: result.expected_output ?? null,
				actual_output: result.stdout || "",
				errors,
			},
		],
	};
}

async function runCode() {
	if (!problem.value || busy.value) return;

	const current = ++generation;

	running.value = true;
	clearResults();
	activeTab.value = "result";

	try {
		const caseIndex = activeCaseIndex.value;
		const input = testCases.value[caseIndex]?.input || "";

		const queued = await dsaApi(
			"run_code",
			{
				problem: problem.value.name,
				code: code.value,
				stdin: input,
				language_id: languageId.value,
				test_case_index: caseIndex + 1,
			},
			{ methodType: "POST" }
		);

		for (let attempt = 0; attempt < 30; attempt += 1) {
			if (disposed || generation !== current) return;

			const result = await dsaApi("get_run_result", { token: queued.token });

			if (disposed || generation !== current) return;

			if (!result.pending) {
				outcome.value = buildRunOutcome(queued, result, caseIndex, input);
				return;
			}

			await wait(1000);
		}

		throw new Error(__("Execution timed out."));
	} catch (err) {
		if (!disposed && generation === current) showError(err);
	} finally {
		if (!disposed) running.value = false;
	}
}

function buildSubmitOutcome(queued, result) {
	const complexity = {
		time: result.time_complexity || queued.complexity || "",
		space: result.space_complexity || queued.space_complexity || "",
		timeResult: result.complexity_result || queued.complexity_result || "",
		spaceResult: result.space_complexity_result || queued.space_complexity_result || "",
	};

	const rejection = complexityRejectionLabel(complexity.timeResult, complexity.spaceResult);

	const cases = (result.results || []).map((row) => ({
		index: row.index,
		status: rejection || row.status,
		input: row.input || "",
		expected_output: row.expected_output ?? null,
		actual_output: row.actual_output || "",
		errors: row.error ? [{ label: classifyError(row.error), text: row.error }] : [],
	}));

	let label;

	if (rejection) {
		label = rejection;
	} else if (result.pending) {
		label = __("Running");
	} else {
		label = displayStatus(result.display_status || result.status);

		const failedWithError = cases.find(
			(testCase) => testCase.status !== "Accepted" && testCase.errors.length
		);

		if (label === __("Wrong Answer") && failedWithError) {
			label = failedWithError.errors[0].label;
		}
	}

	return {
		kind: "submit",
		pending: Boolean(result.pending),
		label,
		tone: rejection ? "danger" : toneFor(label),
		runtime: result.runtime ? formatRuntime(result.runtime) : "",
		memory: result.memory ? formatMemory(result.memory) : "",
		passed: result.passed_count || 0,
		total: result.total_count || 0,
		xp: result.pending ? null : result.xp || null,
		complexity,
		cases,
	};
}

async function submitCode() {
	if (!problem.value || busy.value) return;

	const current = ++generation;

	submitting.value = true;
	clearResults();
	activeTab.value = "result";

	try {
		const queued = await dsaApi(
			"submit_code",
			{
				problem: problem.value.name,
				code: code.value,
				language_id: languageId.value,
			},
			{ methodType: "POST" }
		);

		for (let attempt = 0; attempt < 60; attempt += 1) {
			if (disposed || generation !== current) return;

			const result = await dsaApi(
				"get_submission_result",
				{ submission: queued.submission },
				{ methodType: "POST" }
			);

			if (disposed || generation !== current) return;

			outcome.value = buildSubmitOutcome(queued, result);

			if (!result.pending) {
				const firstFailed = outcome.value.cases.findIndex(
					(testCase) => testCase.status !== "Accepted"
				);
				activeResultCaseIndex.value = firstFailed === -1 ? 0 : firstFailed;

				if (result.status === "Accepted") {
					problem.value.solved = true;
				}

				applyXpToast(result);

				return;
			}

			await wait(1000);
		}

		throw new Error(__("Submission timed out."));
	} catch (err) {
		if (!disposed && generation === current) showError(err);
	} finally {
		if (!disposed) submitting.value = false;
	}
}

onMounted(loadProblem);

watch(
	() => props.problem,
	(next, previous) => {
		if (next && next !== previous) loadProblem();
	}
);

watch(languageId, () => {
	if (solutionLoading.value) return;

	solutionError.value = "";
	solutionErrorKind.value = "";

	if (activeTab.value === "solution" && solutionFree.value && problem.value) {
		requestSolution();
	}
});

watch(showSolutionConfirm, (isOpen) => {
	if (isOpen) {
		nextTick(() => solutionCancelButton.value?.focus());
	}
});

onBeforeUnmount(() => {
	disposed = true;
	generation += 1;
	solutionRequestId += 1;
	clearTimeout(xpToastTimer);
	xpToastTimer = null;
});

defineExpose({
	layout: () => monacoEditor.value?.layout(),
});
</script>

<style scoped>
.cp-root {
	width: 100%;
	max-width: 100%;
	min-width: 0;
	margin: 12px 0;
}

.cp-page-title {
	margin: 0 0 10px 2px;
	color: var(--text-muted, color-mix(in srgb, currentColor 62%, transparent));
	font-size: 20px;
	font-weight: 700;
	letter-spacing: 0.08em;
	line-height: 1.3;
	text-transform: uppercase;
}

.coding-problem {
	--cp-border: var(--border-color, color-mix(in srgb, currentColor 18%, transparent));
	--cp-bg: var(--card-bg, transparent);
	--cp-head-bg: var(--control-bg, color-mix(in srgb, currentColor 5%, transparent));
	--cp-hover: var(--fg-hover-color, color-mix(in srgb, currentColor 10%, transparent));
	--cp-muted: var(--text-muted, color-mix(in srgb, currentColor 62%, transparent));

	--cp-blue: var(--text-on-blue, #2563eb);
	--cp-green: var(--text-on-green, #16a34a);
	--cp-red: var(--text-on-red, #dc2626);
	--cp-orange: var(--text-on-orange, #d97706);
	--cp-purple: var(--text-on-purple, #7c3aed);
	--cp-focus: var(--primary, var(--cp-blue));

	--cp-optimal: var(--color-optimal, #28c76f);
	--cp-too-complex: var(--color-too-complex, #e05757);

	--cp-option-bg: var(--control-bg, #ffffff);
	--cp-option-fg: var(--text-color, #222222);
	--cp-mono: var(
		--font-stack-monospace,
		ui-monospace,
		SFMono-Regular,
		Menlo,
		Consolas,
		monospace
	);

	container-type: inline-size;
	width: 100%;
	max-width: 100%;
	min-width: 0;
	margin: 0;
	overflow: hidden;
	border: 1px solid var(--cp-border);
	border-radius: 10px;
	background: var(--cp-bg);
	color: inherit;
	font-size: 13px;
	line-height: 1.5;
	text-align: left;
}

:global([data-theme="dark"]) .coding-problem,
:global([data-theme-mode="dark"]) .coding-problem,
:global(.dark) .coding-problem {
	--cp-blue: var(--text-on-blue, #6ea8fe);
	--cp-green: var(--text-on-green, #5fd68a);
	--cp-red: var(--text-on-red, #ff6b6b);
	--cp-orange: var(--text-on-orange, #f5b84b);
	--cp-purple: var(--text-on-purple, #b78cff);
	--cp-option-bg: var(--control-bg, #252525);
	--cp-option-fg: var(--text-color, #e6e6e6);
}

.coding-problem *,
.coding-problem *::before,
.coding-problem *::after {
	box-sizing: border-box;
}

.coding-problem button,
.coding-problem select,
.coding-problem textarea {
	font-family: inherit;
	color: inherit;
}

.coding-problem button:focus-visible,
.coding-problem select:focus-visible,
.coding-problem textarea:focus-visible {
	outline: 2px solid var(--cp-focus);
	outline-offset: 2px;
}

.cp-sr-only {
	position: absolute;
	width: 1px;
	height: 1px;
	overflow: hidden;
	clip: rect(0, 0, 0, 0);
	white-space: nowrap;
}

.cp-header {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	justify-content: space-between;
	gap: 8px 14px;
	padding: 12px 14px;
	background: var(--cp-head-bg);
}

.cp-heading {
	display: flex;
	min-width: 0;
	align-items: center;
	gap: 8px;
}

.cp-glyph {
	flex-shrink: 0;
	color: var(--cp-green);
	font-family: var(--cp-mono);
	font-size: 13px;
	font-weight: 700;
}

.cp-title {
	min-width: 0;
	margin: 0;
	font-size: 16px;
	font-weight: 650;
	line-height: 1.3;
	overflow-wrap: anywhere;
}

.cp-badges {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 6px;
}

.cp-badge {
	display: inline-flex;
	align-items: center;
	padding: 3px 9px;
	border-radius: 12px;
	background: color-mix(in srgb, currentColor 8%, transparent);
	font-size: 11px;
	font-weight: 600;
	line-height: 1.3;
	text-transform: capitalize;
}

.cp-difficulty.is-easy {
	background: color-mix(in srgb, var(--cp-green) 16%, transparent);
	color: var(--cp-green);
}

.cp-difficulty.is-medium {
	background: color-mix(in srgb, var(--cp-orange) 16%, transparent);
	color: var(--cp-orange);
}

.cp-difficulty.is-hard {
	background: color-mix(in srgb, var(--cp-red) 16%, transparent);
	color: var(--cp-red);
}

.cp-badge-xp {
	color: var(--cp-orange);
	font-variant-numeric: tabular-nums;
	text-transform: none;
}

.cp-badge-solved {
	color: var(--cp-green);
}

.cp-link-btn {
	display: inline-flex;
	align-items: center;
	gap: 4px;
	padding: 3px 4px;
	border: 0;
	border-radius: 4px;
	background: transparent;
	color: var(--cp-muted);
	font-size: 11px;
	cursor: pointer;
}

.cp-link-btn:hover {
	color: inherit;
}

.cp-chevron {
	width: 14px;
	height: 14px;
	flex-shrink: 0;
	transition: transform 0.15s ease;
}

.cp-chevron.is-open {
	transform: rotate(180deg);
}

.cp-section-toggle .cp-chevron.is-open {
	transform: rotate(90deg);
}

.cp-skeleton {
	padding: 18px 14px;
}

.cp-skeleton span {
	display: block;
	height: 10px;
	margin-bottom: 12px;
	border-radius: 5px;
	background: var(--cp-head-bg);
	animation: cp-pulse 1.2s ease-in-out infinite;
}

@keyframes cp-pulse {
	50% {
		opacity: 0.45;
	}
}

.cp-load-error {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	justify-content: space-between;
	gap: 10px;
	margin: 12px;
	padding: 12px 14px;
	border: 1px solid color-mix(in srgb, var(--cp-red) 45%, transparent);
	border-radius: 8px;
	background: color-mix(in srgb, var(--cp-red) 9%, transparent);
	color: var(--cp-red);
}

.cp-problem {
	max-height: 460px;
	overflow-y: auto;
	padding: 12px 14px 4px;
	border-top: 1px solid var(--cp-border);
	overscroll-behavior: contain;
}

.cp-facts {
	display: flex;
	flex-wrap: wrap;
	gap: 6px;
	margin-bottom: 10px;
}

.cp-chip {
	display: inline-flex;
	align-items: center;
	gap: 5px;
	padding: 3px 9px;
	border: 1px solid var(--cp-border);
	border-radius: 999px;
	background: var(--cp-head-bg);
	font-size: 11px;
	font-variant-numeric: tabular-nums;
	line-height: 1.4;
}

.cp-chip-topic {
	border-color: transparent;
	background: color-mix(in srgb, var(--cp-blue) 14%, transparent);
	color: var(--cp-blue);
}

.cp-k {
	color: var(--cp-muted);
	font-weight: 600;
}

.cp-section {
	margin-bottom: 8px;
	padding-bottom: 8px;
	border-bottom: 1px solid var(--cp-border);
}

.cp-section:last-child {
	border-bottom: 0;
}

.cp-section-toggle {
	display: flex;
	width: 100%;
	align-items: center;
	gap: 4px;
	padding: 4px 0;
	border: 0;
	background: transparent;
	font-size: 13px;
	font-weight: 650;
	text-align: left;
	cursor: pointer;
}

.cp-rich {
	padding: 4px 0 6px 18px;
	font-size: 13.5px;
	line-height: 1.65;
	overflow-wrap: anywhere;
}

.cp-rich :deep(*) {
	max-width: 100%;
}

.cp-rich :deep(:where(p, span, div, li, ul, ol, strong, em, b, i, h1, h2, h3, h4, h5, h6, td, th)) {
	color: inherit !important;
	background-color: transparent !important;
}

.cp-rich :deep(p) {
	margin: 0 0 0.6em;
}

.cp-rich :deep(p:last-child) {
	margin-bottom: 0;
}

.cp-rich :deep(ul),
.cp-rich :deep(ol) {
	margin: 0.4em 0;
	padding-left: 1.4em;
}

.cp-rich :deep(a) {
	color: var(--cp-blue);
}

.cp-rich :deep(img) {
	height: auto;
}

.cp-rich :deep(table) {
	display: block;
	overflow-x: auto;
	border-collapse: collapse;
}

.cp-rich :deep(td),
.cp-rich :deep(th) {
	padding: 4px 8px;
	border: 1px solid var(--cp-border);
}

.cp-rich :deep(pre) {
	margin: 0.5em 0;
	padding: 8px 12px;
	overflow-x: auto;
	border: 0;
	border-left: 2px solid var(--cp-border);
	border-radius: 0;
	background: transparent;
	color: inherit;
	font-family: var(--cp-mono);
	font-size: 12.5px;
	white-space: pre-wrap;
}

.cp-rich :deep(code) {
	padding: 1px 5px;
	border: 1px solid var(--cp-border);
	border-radius: 5px;
	background: var(--cp-head-bg);
	color: inherit;
	font-family: var(--cp-mono);
	font-size: 0.92em;
}

.cp-rich :deep(pre code) {
	padding: 0;
	border: 0;
	background: transparent;
}

.cp-workspace {
	display: grid;
	gap: 10px;
	padding: 12px;
	border-top: 1px solid var(--cp-border);
}

.cp-card {
	min-width: 0;
	overflow: hidden;
	border: 1px solid var(--cp-border);
	border-radius: 8px;
	background: var(--cp-bg);
}

.cp-toolbar {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	justify-content: space-between;
	gap: 8px;
	padding: 7px 10px;
	border-bottom: 1px solid var(--cp-border);
	background: var(--cp-head-bg);
}

.cp-toolbar-group {
	display: flex;
	align-items: center;
	gap: 6px;
}

.cp-lang {
	position: relative;
	display: inline-flex;
	height: 30px;
	align-items: center;
	border: 1px solid var(--cp-border);
	border-radius: 6px;
	background: var(--cp-bg);
}

.cp-lang:hover {
	background: var(--cp-hover);
}

.cp-lang:focus-within {
	outline: 2px solid var(--cp-focus);
	outline-offset: 1px;
}

.cp-lang select {
	height: 100%;
	padding: 0 26px 0 10px;
	border: 0;
	outline: none;
	appearance: none;
	background: transparent;
	font-size: 12px;
	font-weight: 600;
	cursor: pointer;
}

.cp-lang select:disabled {
	cursor: wait;
	opacity: 0.6;
}

.cp-lang select option {
	background: var(--cp-option-bg);
	color: var(--cp-option-fg);
}

.cp-lang-chevron {
	position: absolute;
	right: 8px;
	width: 13px;
	height: 13px;
	color: var(--cp-muted);
	pointer-events: none;
}

.cp-icon-btn {
	display: inline-flex;
	width: 30px;
	height: 30px;
	align-items: center;
	justify-content: center;
	border: 1px solid transparent;
	border-radius: 6px;
	background: transparent;
	color: var(--cp-muted);
	cursor: pointer;
}

.cp-icon-btn svg {
	width: 15px;
	height: 15px;
}

.cp-icon-btn:hover:not(:disabled) {
	background: var(--cp-hover);
	color: inherit;
}

.cp-icon-btn:disabled {
	cursor: not-allowed;
	opacity: 0.5;
}

.cp-btn {
	display: inline-flex;
	height: 30px;
	align-items: center;
	gap: 6px;
	padding: 0 13px;
	border: 1px solid transparent;
	border-radius: 6px;
	font-size: 12px;
	font-weight: 600;
	white-space: nowrap;
	cursor: pointer;
	transition:
		background-color 0.15s ease,
		border-color 0.15s ease,
		box-shadow 0.15s ease,
		transform 0.05s ease;
}

.cp-btn:active:not(:disabled) {
	transform: translateY(1px);
}

.cp-btn:disabled {
	cursor: not-allowed;
	opacity: 0.55;
}

.cp-btn-icon {
	width: 13px;
	height: 13px;
	flex-shrink: 0;
}

.cp-run {
	border-color: var(--cp-border);
	background: var(--cp-bg);
}

.cp-run:hover:not(:disabled) {
	background: var(--cp-hover);
}

.cp-submit {
	border-color: #1c7a43;
	background: #1e8e4d;
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.18);
	color: #fff;
}

.cp-submit:hover:not(:disabled) {
	background: #24a45a;
}

.cp-submit:active:not(:disabled) {
	background: #1b7d44;
	box-shadow: none;
}

.cp-spinner {
	display: inline-block;
	width: 12px;
	height: 12px;
	flex-shrink: 0;
	border: 2px solid currentColor;
	border-top-color: transparent;
	border-radius: 50%;
	opacity: 0.75;
	animation: cp-spin 0.7s linear infinite;
}

@keyframes cp-spin {
	to {
		transform: rotate(360deg);
	}
}

.cp-editor-area {
	height: clamp(240px, 42vh, 420px);
	min-height: 180px;
	max-height: 80vh;
	overflow: hidden;
	resize: vertical;
}

.cp-terminal {
	color: inherit;
}

.cp-terminal-header {
	display: flex;
	height: 42px;
	align-items: center;
	justify-content: space-between;
	padding: 0 12px;
	border-bottom: 1px solid var(--cp-border);
	background: var(--cp-head-bg);
}

.cp-result-tabs {
	display: flex;
	height: 100%;
	align-items: stretch;
	gap: 18px;
}

.cp-result-tabs > button {
	display: flex;
	align-items: center;
	gap: 6px;
	padding: 0;
	border: 0;
	background: transparent;
	color: var(--cp-muted);
	font-size: 12px;
	cursor: pointer;
}

.cp-result-tabs > button + button {
	position: relative;
}

.cp-result-tabs > button + button::before {
	position: absolute;
	top: 50%;
	left: -10px;
	width: 1px;
	height: 18px;
	background: var(--cp-hover);
	content: "";
	transform: translateY(-50%);
}

.cp-result-tabs .is-active {
	color: inherit;
}

.cp-terminal-header > button {
	border: 0;
	background: transparent;
	color: var(--cp-muted);
	font-size: 11px;
	cursor: pointer;
}

.cp-terminal-header > button:hover {
	color: inherit;
}

.cp-green {
	color: var(--cp-green);
}

.cp-tab-glyph {
	font-family: var(--font-stack, inherit);
	font-size: 12px;
	font-variant-emoji: text;
	line-height: 1;
}

.cp-solution-tab-icon {
	width: 14px;
	height: 14px;
	flex-shrink: 0;
	color: inherit;
}

.cp-result-tabs > button.is-active .cp-solution-tab-icon {
	color: var(--cp-blue);
}

.cp-terminal-body {
	position: relative;
	max-height: 380px;
	min-height: 120px;
	overflow: auto;
	padding: 14px 16px;
	font-family: var(--cp-mono);
	font-size: 12px;
	overscroll-behavior: contain;
}

.cp-terminal-body pre {
	margin: 0;
	background: transparent;
	color: inherit;
	font-family: inherit;
	white-space: pre-wrap;
	overflow-wrap: anywhere;
}

.cp-muted {
	color: var(--cp-muted);
}

.cp-empty-result {
	position: absolute;
	inset: 0;
	display: grid;
	place-items: center;
	color: var(--cp-muted);
	font-family: inherit;
}

.cp-testcase {
	display: flex;
	min-height: 100%;
	flex-direction: column;
	gap: 10px;
}

.cp-testcase label {
	margin: 0;
	color: inherit;
	font-size: 11px;
	font-weight: 600;
}

.cp-testcase textarea {
	width: 100%;
	min-height: 105px;
	padding: 12px;
	resize: vertical;
	border: 1px solid var(--cp-border);
	border-radius: 7px;
	outline: none;
	background: var(--cp-head-bg);
	font: inherit;
}

.cp-testcase textarea:focus {
	border-color: #4b8bf5;
}

.cp-case-tabs {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 8px;
	margin-bottom: 6px;
}

.cp-case-tabs button {
	display: inline-flex;
	align-items: center;
	gap: 7px;
	height: 34px;
	padding: 0 14px;
	border: 0;
	border-radius: 7px;
	background: transparent;
	color: var(--cp-muted);
	font-size: 12px;
	cursor: pointer;
}

.cp-case-tabs button:hover {
	background: var(--cp-head-bg);
	color: inherit;
}

.cp-case-tabs button.is-active {
	background: var(--cp-hover);
	color: inherit;
}

.cp-case-tabs .cp-add-case {
	padding: 0 11px;
	color: var(--cp-muted);
	font-size: 20px;
}

.cp-result-cases {
	margin-bottom: 16px;
}

.cp-case-pass {
	color: var(--cp-green);
	font-size: 9px;
}

.cp-case-fail {
	color: var(--cp-red);
	font-size: 9px;
}

.cp-results {
	font-family: inherit;
}

.cp-result-summary {
	display: flex;
	flex-wrap: wrap;
	align-items: baseline;
	gap: 6px 14px;
	margin-bottom: 18px;
}

.cp-result-summary strong {
	color: var(--cp-red);
	font-size: 20px;
	font-weight: 500;
}

.cp-result-summary strong.is-success {
	color: var(--cp-green);
}

.cp-result-summary strong.is-pending {
	color: var(--cp-muted);
}

.cp-result-summary span {
	color: var(--cp-muted);
}

.cp-xp-line {
	display: flex;
	flex-wrap: wrap;
	align-items: baseline;
	gap: 12px;
	margin: -8px 0 16px;
	color: var(--cp-muted);
	font-size: 12px;
}

.cp-xp-line strong {
	color: var(--cp-orange);
	font-size: 14px;
	font-weight: 700;
}

.cp-xp-line.is-error {
	color: var(--cp-orange);
}

.cp-complexity-info {
	display: flex;
	flex-wrap: wrap;
	gap: 10px 24px;
	margin-bottom: 18px;
	padding: 10px 14px;
	border: 1px solid var(--cp-border);
	border-radius: 7px;
	background: var(--cp-head-bg);
}

.cp-complexity-row {
	display: flex;
	align-items: baseline;
	gap: 8px;
	font-size: 12px;
}

.cp-complexity-row label {
	margin: 0;
	color: var(--cp-muted);
	font-weight: 600;
}

.cp-complexity-row > span {
	color: inherit;
}

.cp-complexity-value {
	font-family: var(--cp-mono);
	font-weight: 600;
}

.cp-complexity-result {
	display: inline-flex;
	align-items: center;
	gap: 3px;
	margin-left: 6px;
	font-weight: 500;
}

.cp-complexity-icon {
	font-size: 0.95em;
	line-height: 1;
}

.cp-complexity-value.optimal,
.cp-complexity-result.optimal {
	color: var(--cp-optimal);
}

.cp-complexity-value.too-complex,
.cp-complexity-result.too-complex {
	color: var(--cp-too-complex);
	font-weight: 600;
}

.cp-complexity-result.unknown .cp-complexity-icon {
	display: none;
}

.cp-result-details {
	display: grid;
	gap: 8px;
}

.cp-result-details label {
	margin: 4px 0 0;
	color: var(--cp-muted);
	font-size: 11px;
}

.cp-result-details pre {
	min-height: 54px;
	padding: 12px;
	border-radius: 7px;
	background: var(--cp-head-bg);
	color: inherit;
}

.cp-result-details pre.is-error {
	color: var(--cp-red);
}

.cp-solution-output {
	display: flex;
	min-height: 120px;
	flex-direction: column;
	font-family: var(--font-stack, inherit);
}

.cp-solution-viewer {
	display: flex;
	min-height: 0;
	flex: 1;
	flex-direction: column;
	overflow: hidden;
	border: 1px solid var(--cp-border);
	border-radius: 8px;
	background: var(--cp-head-bg);
}

.cp-solution-header {
	display: flex;
	flex: 0 0 auto;
	align-items: center;
	justify-content: space-between;
	gap: 12px;
	padding: 9px 14px;
	border-bottom: 1px solid var(--cp-border);
	background: var(--cp-bg);
}

.cp-solution-title {
	display: flex;
	align-items: center;
	gap: 7px;
	font-size: 13px;
	font-weight: 600;
}

.cp-solution-title svg {
	width: 15px;
	height: 15px;
	flex-shrink: 0;
	color: var(--cp-blue);
}

.cp-solution-subtitle {
	margin: 2px 0 0 22px;
	color: var(--cp-muted);
	font-size: 11px;
}

.cp-solution-language {
	padding: 3px 10px;
	border: 1px solid var(--cp-border);
	border-radius: 999px;
	background: var(--cp-head-bg);
	color: var(--cp-blue);
	font-size: 11px;
	font-weight: 600;
	white-space: nowrap;
}

.cp-solution-code {
	max-height: 300px;
	min-height: 0;
	flex: 1;
	overflow: auto;
	outline: none;
}

.cp-solution-code:focus-visible {
	box-shadow: inset 0 0 0 2px var(--cp-focus);
}

.cp-terminal-body .cp-solution-code pre {
	min-width: max-content;
	margin: 0;
	padding: 14px 16px;
	overflow: visible;
	border: 0;
	border-radius: 0;
	background: transparent;
	color: inherit;
	font-family: var(--cp-mono);
	font-size: 12.5px;
	line-height: 1.65;
	overflow-wrap: normal;
	tab-size: 4;
	white-space: pre;
}

.cp-terminal-body .cp-solution-code code {
	padding: 0;
	border: 0;
	background: none;
	color: inherit;
	font: inherit;
	white-space: inherit;
}

.cp-solution-state {
	display: flex;
	min-height: 160px;
	flex: 1;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 6px;
	padding: 12px;
	color: var(--cp-muted);
	font-size: 12px;
	text-align: center;
}

.cp-solution-state strong {
	color: inherit;
	font-size: 13px;
	font-weight: 600;
}

.cp-solution-state p {
	max-width: 380px;
	margin: 0;
	line-height: 1.5;
}

.cp-solution-state-icon {
	width: 26px;
	height: 26px;
	color: var(--cp-blue);
}

.cp-solution-state.is-error strong {
	color: var(--cp-red);
}

.cp-solution-spinner {
	display: inline-block;
	width: 22px;
	height: 22px;
	flex-shrink: 0;
	margin-top: 6px;
	border: 2px solid var(--cp-border);
	border-top-color: var(--cp-blue);
	border-radius: 50%;
	animation: cp-solution-spin 0.8s linear infinite;
}

.cp-solution-spinner.is-small {
	width: 12px;
	height: 12px;
	margin-top: 0;
	border-color: currentColor;
	border-top-color: transparent;
	opacity: 0.8;
}

@keyframes cp-solution-spin {
	to {
		transform: rotate(360deg);
	}
}

.cp-solution-button {
	display: inline-flex;
	height: 32px;
	align-items: center;
	justify-content: center;
	gap: 7px;
	margin-top: 6px;
	padding: 0 16px;
	border: 1px solid var(--cps-border, var(--cp-border));
	border-radius: 7px;
	background: var(--cps-control, var(--cp-head-bg));
	color: var(--cps-text, inherit);
	font-family: inherit;
	font-size: 12px;
	font-weight: 600;
	cursor: pointer;
}

.cp-solution-button:hover:not(:disabled) {
	background: var(--cps-hover, var(--cp-hover));
}

.cp-solution-button:focus-visible {
	outline: 2px solid var(--cps-focus, var(--cp-focus));
	outline-offset: 2px;
}

.cp-solution-button:disabled {
	cursor: not-allowed;
	opacity: 0.55;
}

.cp-solution-button.is-primary {
	border-color: #2a62c4;
	background: #2f6fe4;
	color: #fff;
}

.cp-solution-button.is-primary:hover:not(:disabled) {
	background: #3b7bf0;
}

.cp-solution-modal-backdrop {
	--cps-border: var(--border-color, #3a3a3a);
	--cps-bg: var(--card-bg, #1e1e1e);
	--cps-control: var(--control-bg, #252525);
	--cps-hover: var(--fg-hover-color, #303030);
	--cps-text: var(--text-color, #e6e6e6);
	--cps-muted: var(--text-muted, #999999);
	--cps-blue: var(--text-on-blue, #6ea8fe);
	--cps-orange: var(--text-on-orange, #f5b84b);
	--cps-red: var(--text-on-red, #ff6b6b);
	--cps-focus: var(--primary, var(--cps-blue));

	position: fixed;
	inset: 0;
	z-index: 2100;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 16px;
	background: rgba(0, 0, 0, 0.55);
}

.cp-solution-modal {
	display: flex;
	width: min(400px, 100%);
	flex-direction: column;
	align-items: center;
	padding: 28px 28px 22px;
	border: 1px solid var(--cps-border);
	border-radius: 14px;
	background: var(--cps-bg);
	box-shadow: 0 24px 60px rgba(0, 0, 0, 0.4);
	color: var(--cps-text);
	font-family: var(--font-stack, inherit);
	font-size: 13px;
	line-height: 1.5;
	text-align: center;
}

.cp-solution-modal *,
.cp-solution-modal *::before,
.cp-solution-modal *::after {
	box-sizing: border-box;
}

.cp-solution-modal-icon {
	display: grid;
	width: 56px;
	height: 56px;
	place-items: center;
	margin-bottom: 14px;
	border-radius: 50%;
	background: rgba(75, 139, 245, 0.14);
	color: var(--cps-blue);
}

.cp-solution-modal-icon svg {
	width: 28px;
	height: 28px;
}

.cp-solution-modal h2 {
	margin: 0 0 14px;
	color: var(--cps-text);
	font-size: 18px;
	font-weight: 650;
}

.cp-solution-modal-lead {
	margin: 0;
	color: var(--cps-muted);
	font-size: 13px;
}

.cp-solution-modal-cost {
	margin: 2px 0 8px;
	color: var(--cps-orange);
	font-size: 40px;
	font-variant-numeric: tabular-nums;
	font-weight: 700;
	line-height: 1.2;
}

.cp-solution-modal-cost span {
	margin-left: 6px;
	font-size: 18px;
	font-weight: 600;
}

.cp-solution-modal-balance {
	margin: 0 0 10px;
	color: var(--cps-muted);
	font-size: 12px;
}

.cp-solution-modal-balance strong {
	color: var(--cps-text);
	font-variant-numeric: tabular-nums;
}

.cp-solution-modal-note {
	max-width: 300px;
	margin: 0 0 4px;
	color: var(--cps-muted);
	font-size: 12px;
	line-height: 1.5;
}

.cp-solution-modal-warning {
	max-width: 320px;
	margin: 8px 0 0;
	color: var(--cps-orange);
	font-size: 12px;
	line-height: 1.5;
}

.cp-solution-modal-error {
	display: flex;
	width: 100%;
	flex-direction: column;
	gap: 3px;
	margin-top: 12px;
	padding: 10px 12px;
	border: 1px solid var(--cps-red);
	border-radius: 8px;
	background: rgba(220, 38, 38, 0.08);
	font-size: 12px;
	line-height: 1.45;
	text-align: left;
}

.cp-solution-modal-error strong {
	color: var(--cps-red);
}

.cp-solution-modal-actions {
	display: flex;
	width: 100%;
	justify-content: center;
	gap: 10px;
	margin-top: 16px;
}

.cp-solution-modal-actions .cp-solution-button {
	min-width: 120px;
	margin-top: 0;
}

.cp-solution-modal-fade-enter-active,
.cp-solution-modal-fade-leave-active {
	transition: opacity 0.18s ease;
}

.cp-solution-modal-fade-enter-from,
.cp-solution-modal-fade-leave-to {
	opacity: 0;
}

.dsa-xp-toast {
	position: fixed;
	right: 20px;
	bottom: 20px;
	z-index: 2000;
	display: flex;
	align-items: center;
	gap: 12px;
	min-width: 190px;
	padding: 12px 16px;
	border: 1px solid var(--border-color, #3a3a3a);
	border-left: 3px solid var(--text-on-orange, #f5b84b);
	border-radius: 10px;
	background: var(--card-bg, #1e1e1e);
	color: var(--text-color, #e6e6e6);
	box-shadow: 0 10px 30px rgba(0, 0, 0, 0.28);
	cursor: pointer;
}

.dsa-xp-toast-icon {
	color: var(--text-on-orange, #f5b84b);
	font-size: 20px;
	line-height: 1;
}

.dsa-xp-toast-body {
	display: flex;
	flex-direction: column;
	gap: 2px;
}

.dsa-xp-toast-body strong {
	color: var(--text-on-orange, #f5b84b);
	font-size: 17px;
	font-variant-numeric: tabular-nums;
	font-weight: 700;
	line-height: 1.2;
}

.dsa-xp-toast-body span {
	color: var(--text-muted, #999);
	font-size: 12px;
}

.dsa-xp-toast-enter-active,
.dsa-xp-toast-leave-active {
	transition:
		opacity 0.25s ease,
		transform 0.25s ease;
}

.dsa-xp-toast-enter-from,
.dsa-xp-toast-leave-to {
	opacity: 0;
	transform: translateY(12px);
}

@container (max-width: 520px) {
	.cp-header {
		padding: 10px 12px;
	}

	.cp-problem {
		padding-right: 12px;
		padding-left: 12px;
	}

	.cp-workspace {
		padding: 8px;
	}

	.cp-rich {
		padding-left: 4px;
	}

	.cp-toolbar {
		padding: 6px 8px;
	}

	.cp-btn {
		padding: 0 10px;
	}

	.cp-result-summary strong {
		font-size: 16px;
	}

	.cp-complexity-info {
		flex-direction: column;
		gap: 8px;
	}
}

@media (prefers-reduced-motion: reduce) {
	.cp-skeleton span,
	.cp-spinner {
		animation-duration: 2s;
	}

	.cp-solution-spinner {
		animation-duration: 2s;
	}

	.cp-chevron,
	.cp-btn {
		transition: none;
	}

	.cp-solution-modal-fade-enter-active,
	.cp-solution-modal-fade-leave-active {
		transition: none;
	}

	.dsa-xp-toast-enter-active,
	.dsa-xp-toast-leave-active {
		transition: none;
	}
}

@media (max-width: 480px) {
	.dsa-xp-toast {
		right: 12px;
		bottom: 12px;
		left: 12px;
	}
}
</style>