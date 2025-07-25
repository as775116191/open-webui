<script lang="ts">
	import { getContext, onMount } from 'svelte';
	const i18n = getContext('i18n');

	import Switch from '$lib/components/common/Switch.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Minus from '$lib/components/icons/Minus.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';

	// Store imports
	import { models } from '$lib/stores';

	let selectedModelId = '';

	$: filterModelIds = permissions.models?.allowed_models || [];

	// Default values for permissions
	const defaultPermissions = {
		workspace: {
			models: false,
			knowledge: false,
			prompts: false,
			tools: false
		},
		sharing: {
			public_models: false,
			public_knowledge: false,
			public_prompts: false,
			public_tools: false
		},
		chat: {
			controls: true,
			file_upload: true,
			delete: true,
			edit: true,
			share: true,
			export: true,
			stt: true,
			tts: true,
			call: true,
			multiple_models: true,
			temporary: true,
			temporary_enforced: false
		},
		features: {
			direct_tool_servers: false,
			web_search: true,
			image_generation: true,
			code_interpreter: true,
			notes: true
		},
		models: {
			allowed_models: []
		}
	};

	export let permissions = {};

	// Reactive statement to ensure all fields are present in `permissions`
	$: {
		permissions = fillMissingProperties(permissions, defaultPermissions);
	}

	function fillMissingProperties(obj: any, defaults: any) {
		return {
			...defaults,
			...obj,
			workspace: { ...defaults.workspace, ...obj.workspace },
			sharing: { ...defaults.sharing, ...obj.sharing },
			chat: { ...defaults.chat, ...obj.chat },
			features: { ...defaults.features, ...obj.features },
			models: { ...defaults.models, ...obj.models }
		};
	}

	onMount(() => {
		permissions = fillMissingProperties(permissions, defaultPermissions);
	});
</script>

<div>
	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Model Permissions')}</div>

		<div class="mb-2">
			<div class=" space-y-1.5">
				<div class="flex flex-col w-full">
					<div class="mb-1 flex justify-between">
						<div class="text-xs text-gray-500">{$i18n.t('允许的模型')}</div>
					</div>

					{#if permissions.models.allowed_models.length > 0}
						<div class="flex flex-col">
							{#each permissions.models.allowed_models as modelId, modelIdx}
								<div class=" flex gap-2 w-full justify-between items-center">
									<div class=" text-sm flex-1 rounded-lg">
										{$models.find(m => m.id === modelId)?.name || modelId}
									</div>
									<div class="shrink-0">
										<button
											type="button"
											on:click={() => {
												permissions.models.allowed_models = permissions.models.allowed_models.filter((_, idx) => idx !== modelIdx);
											}}
										>
											<Minus strokeWidth="2" className="size-3.5" />
										</button>
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<div class="text-gray-500 text-xs text-center py-2 px-10">
							{$i18n.t('未选择模型。用户将有权访问所有模型。')}
						</div>
					{/if}
				</div>
			</div>
			<hr class=" border-gray-100 dark:border-gray-700/10 mt-2.5 mb-1 w-full" />

			<div class="flex items-center gap-2">
				<select
					class="w-full py-1 text-sm rounded-lg bg-transparent {selectedModelId
						? ''
						: 'text-gray-500'} placeholder:text-gray-300 dark:placeholder:text-gray-700 outline-hidden"
					bind:value={selectedModelId}
				>
					<option value="">{$i18n.t('Select a model')}</option>
					{#each $models.filter((m) => m?.owned_by !== 'arena' && !permissions.models.allowed_models.includes(m.id)) as model}
						<option value={model.id} class="bg-gray-50 dark:bg-gray-700">{model.name}</option>
					{/each}
				</select>

				<div>
					<button
						type="button"
						on:click={() => {
							if (selectedModelId && !permissions.models.allowed_models.includes(selectedModelId)) {
								permissions.models.allowed_models = [...permissions.models.allowed_models, selectedModelId];
								selectedModelId = '';
							}
						}}
					>
						<Plus className="size-3.5" strokeWidth="2" />
					</button>
				</div>
			</div>
		</div>
	</div>

	<hr class=" border-gray-100 dark:border-gray-850 my-2" />

	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Workspace Permissions')}</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Models Access')}
			</div>
			<Switch bind:state={permissions.workspace.models} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Knowledge Access')}
			</div>
			<Switch bind:state={permissions.workspace.knowledge} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Prompts Access')}
			</div>
			<Switch bind:state={permissions.workspace.prompts} />
		</div>

		<div class=" ">
			<Tooltip
				className=" flex w-full justify-between my-2 pr-2"
				content={$i18n.t(
					'Warning: Enabling this will allow users to upload arbitrary code on the server.'
				)}
				placement="top-start"
			>
				<div class=" self-center text-xs font-medium">
					{$i18n.t('Tools Access')}
				</div>
				<Switch bind:state={permissions.workspace.tools} />
			</Tooltip>
		</div>
	</div>

	<hr class=" border-gray-100 dark:border-gray-850 my-2" />

	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Sharing Permissions')}</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Models Public Sharing')}
			</div>
			<Switch bind:state={permissions.sharing.public_models} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Knowledge Public Sharing')}
			</div>
			<Switch bind:state={permissions.sharing.public_knowledge} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Prompts Public Sharing')}
			</div>
			<Switch bind:state={permissions.sharing.public_prompts} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Tools Public Sharing')}
			</div>
			<Switch bind:state={permissions.sharing.public_tools} />
		</div>
	</div>

	<hr class=" border-gray-100 dark:border-gray-850 my-2" />

	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Chat Permissions')}</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow File Upload')}
			</div>

			<Switch bind:state={permissions.chat.file_upload} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Chat Controls')}
			</div>

			<Switch bind:state={permissions.chat.controls} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Chat System Prompt')}
			</div>

			<Switch bind:state={permissions.chat.system_prompt} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Chat Delete')}
			</div>

			<Switch bind:state={permissions.chat.delete} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Chat Edit')}
			</div>

			<Switch bind:state={permissions.chat.edit} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Chat Share')}
			</div>

			<Switch bind:state={permissions.chat.share} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Chat Export')}
			</div>

			<Switch bind:state={permissions.chat.export} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Speech to Text')}
			</div>

			<Switch bind:state={permissions.chat.stt} />
		</div>
		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Text to Speech')}
			</div>

			<Switch bind:state={permissions.chat.tts} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Call')}
			</div>

			<Switch bind:state={permissions.chat.call} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Multiple Models in Chat')}
			</div>

			<Switch bind:state={permissions.chat.multiple_models} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Allow Temporary Chat')}
			</div>

			<Switch bind:state={permissions.chat.temporary} />
		</div>

		{#if permissions.chat.temporary}
			<div class="  flex w-full justify-between my-2 pr-2">
				<div class=" self-center text-xs font-medium">
					{$i18n.t('Enforce Temporary Chat')}
				</div>

				<Switch bind:state={permissions.chat.temporary_enforced} />
			</div>
		{/if}
	</div>

	<hr class=" border-gray-100 dark:border-gray-850 my-2" />

	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Features Permissions')}</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Direct Tool Servers')}
			</div>

			<Switch bind:state={permissions.features.direct_tool_servers} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Web Search')}
			</div>

			<Switch bind:state={permissions.features.web_search} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Image Generation')}
			</div>

			<Switch bind:state={permissions.features.image_generation} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Code Interpreter')}
			</div>

			<Switch bind:state={permissions.features.code_interpreter} />
		</div>

		<div class="  flex w-full justify-between my-2 pr-2">
			<div class=" self-center text-xs font-medium">
				{$i18n.t('Notes')}
			</div>

			<Switch bind:state={permissions.features.notes} />
		</div>
	</div>
</div>
