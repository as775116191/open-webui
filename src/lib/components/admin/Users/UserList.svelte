<script>
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { WEBUI_NAME, config, user, showSidebar } from '$lib/stores';
	import { goto } from '$app/navigation';
	import { onMount, getContext } from 'svelte';

	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	import localizedFormat from 'dayjs/plugin/localizedFormat';
	dayjs.extend(relativeTime);
	dayjs.extend(localizedFormat);

	import { toast } from 'svelte-sonner';

	import { updateUserRole, getUsers, deleteUserById, updateUserTokens, manualTokenGrant } from '$lib/apis/users';
	import { getTokenUsageConfig } from '$lib/apis/configs';

	import Pagination from '$lib/components/common/Pagination.svelte';
	import ChatBubbles from '$lib/components/icons/ChatBubbles.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';

	import EditUserModal from '$lib/components/admin/Users/UserList/EditUserModal.svelte';
	import UserChatsModal from '$lib/components/admin/Users/UserList/UserChatsModal.svelte';
	import AddUserModal from '$lib/components/admin/Users/UserList/AddUserModal.svelte';

	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
	import RoleUpdateConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

	import Badge from '$lib/components/common/Badge.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import About from '$lib/components/chat/Settings/About.svelte';
	import Banner from '$lib/components/common/Banner.svelte';
	import Markdown from '$lib/components/chat/Messages/Markdown.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	const i18n = getContext('i18n');

	let page = 1;

	let users = null;
	let total = null;

	let query = '';
	let orderBy = 'created_at'; // default sort key
	let direction = 'asc'; // default sort order

	let selectedUser = null;

	let showDeleteConfirmDialog = false;
	let showAddUserModal = false;

	let showUserChatsModal = false;
	let showEditUserModal = false;
	let showTokenModal = false;
	let selectedUserTokenData = {
		replenish_interval: 86400,
		replenish_amount: 5000
	};
	let manualTokenAmount = 1000;
	let tokenUsageEnabled = false;

	// Load token usage configuration
	onMount(async () => {
		try {
			const config = await getTokenUsageConfig(localStorage.token);
			tokenUsageEnabled = config?.ENABLE_TOKEN_USAGE_CONTROL || false;
		} catch (err) {
			console.error('Failed to load token usage config:', err);
		}
	});

	const deleteUserHandler = async (id) => {
		const res = await deleteUserById(localStorage.token, id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		// if the user is deleted and the current page has only one user, go back to the previous page
		if (users.length === 1 && page > 1) {
			page -= 1;
		}

		if (res) {
			getUserList();
		}
	};

	const setSortKey = (key) => {
		if (orderBy === key) {
			direction = direction === 'asc' ? 'desc' : 'asc';
		} else {
			orderBy = key;
			direction = 'asc';
		}
	};

	const getUserList = async () => {
		try {
			const res = await getUsers(localStorage.token, query, orderBy, direction, page).catch(
				(error) => {
					toast.error(`${error}`);
					return null;
				}
			);

			if (res) {
				users = res.users;
				total = res.total;
			}
		} catch (err) {
			console.error(err);
		}
	};

	const updateTokensHandler = async (userId, tokenData) => {
		try {
			const res = await updateUserTokens(localStorage.token, userId, tokenData);
			if (res) {
				toast.success($i18n.t('User token settings updated successfully'));
				
				// Update selectedUser data immediately
				if (selectedUser && selectedUser.id === userId) {
					selectedUser.token_replenish_interval = tokenData.replenish_interval;
					selectedUser.token_replenish_amount = tokenData.replenish_amount;
				}
				
				// Refresh the user list
				getUserList();
				showTokenModal = false;
			}
		} catch (error) {
			toast.error(`${error}`);
		}
	};

	const grantTokensHandler = async (userId, amount) => {
		try {
			const res = await manualTokenGrant(localStorage.token, userId, amount);
			if (res) {
				toast.success($i18n.t('Tokens granted successfully'));
				
				// Update selectedUser data immediately
				if (selectedUser && selectedUser.id === userId) {
					selectedUser.token_balance = (selectedUser.token_balance || 0) + amount;
				}
				
				// Refresh the user list
				getUserList();
				manualTokenAmount = 1000;
			}
		} catch (error) {
			toast.error(`${error}`);
		}
	};

	$: if (page) {
		getUserList();
	}

	$: if (query !== null && orderBy && direction) {
		getUserList();
	}
</script>

<ConfirmDialog
	bind:show={showDeleteConfirmDialog}
	on:confirm={() => {
		deleteUserHandler(selectedUser.id);
	}}
/>

{#key selectedUser}
	<EditUserModal
		bind:show={showEditUserModal}
		{selectedUser}
		sessionUser={$user}
		on:save={async () => {
			getUserList();
		}}
	/>
{/key}

<AddUserModal
	bind:show={showAddUserModal}
	on:save={async () => {
		getUserList();
	}}
/>

{#if selectedUser}
	<UserChatsModal bind:show={showUserChatsModal} user={selectedUser} />
{/if}

<!-- Token Management Modal -->
{#if selectedUser && showTokenModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
		<div class="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md mx-4 shadow-xl">
			<div class="flex justify-between items-center mb-4">
				<h2 class="text-lg font-semibold text-gray-900 dark:text-white">
					{$i18n.t('Token 信息')} - {selectedUser.name}
				</h2>
				<button
					class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
					on:click={() => (showTokenModal = false)}
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
					</svg>
				</button>
			</div>

			<div class="space-y-4">
				<div class="text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-800 p-3 rounded">
					<div class="flex justify-between">
						<span>{$i18n.t('当前余额')}:</span>
						<span class="font-semibold {selectedUser.token_balance <= 0 ? 'text-red-500' : 'text-green-600 dark:text-green-400'}">
							{selectedUser.token_balance?.toLocaleString() ?? 0}
						</span>
					</div>
					<div class="flex justify-between mt-1">
						<span>{$i18n.t('总使用量')}:</span>
						<span>{selectedUser.total_tokens_used?.toLocaleString() ?? 0}</span>
					</div>
				</div>

				<div class="grid grid-cols-1 gap-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
							{$i18n.t('Token 补充时间间隔（秒）')}
						</label>
						<input
							type="number"
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
							bind:value={selectedUserTokenData.replenish_interval}
							min="1"
						/>
						<p class="text-xs text-gray-500 mt-1">{$i18n.t('Default: 86400 (24 hours)')}</p>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
							{$i18n.t('Token 补充数量')}
						</label>
						<input
							type="number"
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
							bind:value={selectedUserTokenData.replenish_amount}
							min="0"
						/>
						<p class="text-xs text-gray-500 mt-1">{$i18n.t('Default: 5000')}</p>
					</div>

					<hr class="border-gray-200 dark:border-gray-700" />

					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
							{$i18n.t('手动 token 补充')}
						</label>
						<div class="flex gap-2">
							<input
								type="number"
								class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
								bind:value={manualTokenAmount}
								min="1"
								placeholder="1000"
							/>
							<button
								class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium"
								on:click={() => grantTokensHandler(selectedUser.id, manualTokenAmount)}
							>
								{$i18n.t('补充')}
							</button>
						</div>
						<p class="text-xs text-gray-500 mt-1">{$i18n.t('立即添加 token 到用户余额')}</p>
					</div>
				</div>

				<div class="flex gap-2 pt-4">
					<button
						class="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-md text-sm font-medium"
						on:click={() => (showTokenModal = false)}
					>
						{$i18n.t('取消')}
					</button>
					<button
						class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium"
						on:click={() => updateTokensHandler(selectedUser.id, selectedUserTokenData)}
					>
						{$i18n.t('保存设置')}
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

{#if ($config?.license_metadata?.seats ?? null) !== null && total && total > $config?.license_metadata?.seats}
	<div class=" mt-1 mb-2 text-xs text-red-500">
		<Banner
			className="mx-0"
			banner={{
				type: 'error',
				title: 'License Error',
				content:
					'Exceeded the number of seats in your license. Please contact support to increase the number of seats.',
				dismissable: true
			}}
		/>
	</div>
{/if}

{#if users === null || total === null}
	<div class="my-10">
		<Spinner className="size-5" />
	</div>
{:else}
	<div class="mt-0.5 mb-2 gap-1 flex flex-col md:flex-row justify-between">
		<div class="flex md:self-center text-lg font-medium px-0.5">
			<div class="flex-shrink-0">
				{$i18n.t('Users')}
			</div>
			<div class="flex self-center w-[1px] h-6 mx-2.5 bg-gray-50 dark:bg-gray-850" />

			{#if ($config?.license_metadata?.seats ?? null) !== null}
				{#if total > $config?.license_metadata?.seats}
					<span class="text-lg font-medium text-red-500"
						>{total} of {$config?.license_metadata?.seats}
						<span class="text-sm font-normal">available users</span></span
					>
				{:else}
					<span class="text-lg font-medium text-gray-500 dark:text-gray-300"
						>{total} of {$config?.license_metadata?.seats}
						<span class="text-sm font-normal">available users</span></span
					>
				{/if}
			{:else}
				<span class="text-lg font-medium text-gray-500 dark:text-gray-300">{total}</span>
			{/if}
		</div>

		<div class="flex gap-1">
			<div class=" flex w-full space-x-2">
				<div class="flex flex-1">
					<div class=" self-center ml-1 mr-3">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 20 20"
							fill="currentColor"
							class="w-4 h-4"
						>
							<path
								fill-rule="evenodd"
								d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
								clip-rule="evenodd"
							/>
						</svg>
					</div>
					<input
						class=" w-full text-sm pr-4 py-1 rounded-r-xl outline-hidden bg-transparent"
						bind:value={query}
						placeholder={$i18n.t('Search')}
					/>
				</div>

				<div>
					<Tooltip content={$i18n.t('Add User')}>
						<button
							class=" p-2 rounded-xl hover:bg-gray-100 dark:bg-gray-900 dark:hover:bg-gray-850 transition font-medium text-sm flex items-center space-x-1"
							on:click={() => {
								showAddUserModal = !showAddUserModal;
							}}
						>
							<Plus className="size-3.5" />
						</button>
					</Tooltip>
				</div>
			</div>
		</div>
	</div>

	<div
		class="scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full rounded-sm pt-0.5"
	>
		<table
			class="w-full text-sm text-left text-gray-500 dark:text-gray-400 table-auto max-w-full rounded-sm"
		>
			<thead
				class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-850 dark:text-gray-400 -translate-y-0.5"
			>
				<tr class="">
					<th
						scope="col"
						class="px-3 py-1.5 cursor-pointer select-none"
						on:click={() => setSortKey('role')}
					>
						<div class="flex gap-1.5 items-center">
							{$i18n.t('Role')}

							{#if orderBy === 'role'}
								<span class="font-normal"
									>{#if direction === 'asc'}
										<ChevronUp className="size-2" />
									{:else}
										<ChevronDown className="size-2" />
									{/if}
								</span>
							{:else}
								<span class="invisible">
									<ChevronUp className="size-2" />
								</span>
							{/if}
						</div>
					</th>
					<th
						scope="col"
						class="px-3 py-1.5 cursor-pointer select-none"
						on:click={() => setSortKey('name')}
					>
						<div class="flex gap-1.5 items-center">
							{$i18n.t('Name')}

							{#if orderBy === 'name'}
								<span class="font-normal"
									>{#if direction === 'asc'}
										<ChevronUp className="size-2" />
									{:else}
										<ChevronDown className="size-2" />
									{/if}
								</span>
							{:else}
								<span class="invisible">
									<ChevronUp className="size-2" />
								</span>
							{/if}
						</div>
					</th>
					<th
						scope="col"
						class="px-3 py-1.5 cursor-pointer select-none"
						on:click={() => setSortKey('email')}
					>
						<div class="flex gap-1.5 items-center">
							{$i18n.t('Email')}

							{#if orderBy === 'email'}
								<span class="font-normal"
									>{#if direction === 'asc'}
										<ChevronUp className="size-2" />
									{:else}
										<ChevronDown className="size-2" />
									{/if}
								</span>
							{:else}
								<span class="invisible">
									<ChevronUp className="size-2" />
								</span>
							{/if}
						</div>
					</th>

					<th
						scope="col"
						class="px-3 py-1.5 cursor-pointer select-none"
						on:click={() => setSortKey('last_active_at')}
					>
						<div class="flex gap-1.5 items-center">
							{$i18n.t('Last Active')}

							{#if orderBy === 'last_active_at'}
								<span class="font-normal"
									>{#if direction === 'asc'}
										<ChevronUp className="size-2" />
									{:else}
										<ChevronDown className="size-2" />
									{/if}
								</span>
							{:else}
								<span class="invisible">
									<ChevronUp className="size-2" />
								</span>
							{/if}
						</div>
					</th>
					<th
						scope="col"
						class="px-3 py-1.5 cursor-pointer select-none"
						on:click={() => setSortKey('created_at')}
					>
						<div class="flex gap-1.5 items-center">
							{$i18n.t('Created at')}
							{#if orderBy === 'created_at'}
								<span class="font-normal"
									>{#if direction === 'asc'}
										<ChevronUp className="size-2" />
									{:else}
										<ChevronDown className="size-2" />
									{/if}
								</span>
							{:else}
								<span class="invisible">
									<ChevronUp className="size-2" />
								</span>
							{/if}
						</div>
					</th>

					<th
						scope="col"
						class="px-3 py-1.5 cursor-pointer select-none"
						on:click={() => setSortKey('oauth_sub')}
					>
						<div class="flex gap-1.5 items-center">
							{$i18n.t('OAuth ID')}

							{#if orderBy === 'oauth_sub'}
								<span class="font-normal"
									>{#if direction === 'asc'}
										<ChevronUp className="size-2" />
									{:else}
										<ChevronDown className="size-2" />
									{/if}
								</span>
							{:else}
								<span class="invisible">
									<ChevronUp className="size-2" />
								</span>
							{/if}
						</div>
					</th>

					{#if tokenUsageEnabled}
						<th
							scope="col"
							class="px-3 py-1.5 cursor-pointer select-none"
							on:click={() => setSortKey('token_balance')}
						>
							<div class="flex gap-1.5 items-center">
								{$i18n.t('Token Balance')}

								{#if orderBy === 'token_balance'}
									<span class="font-normal"
										>{#if direction === 'asc'}
											<ChevronUp className="size-2" />
										{:else}
											<ChevronDown className="size-2" />
										{/if}
									</span>
								{:else}
									<span class="invisible">
										<ChevronUp className="size-2" />
									</span>
								{/if}
							</div>
						</th>
					{/if}

					<th scope="col" class="px-3 py-2 text-right" />
				</tr>
			</thead>
			<tbody class="">
				{#each users as user, userIdx}
					<tr class="bg-white dark:bg-gray-900 dark:border-gray-850 text-xs">
						<td class="px-3 py-1 min-w-[7rem] w-28">
							<button
								class=" translate-y-0.5"
								on:click={() => {
									selectedUser = user;
									showEditUserModal = !showEditUserModal;
								}}
							>
								<Badge
									type={user.role === 'admin' ? 'info' : user.role === 'user' ? 'success' : 'muted'}
									content={$i18n.t(user.role)}
								/>
							</button>
						</td>
						<td class="px-3 py-1 font-medium text-gray-900 dark:text-white w-max">
							<div class="flex flex-row w-max">
								<img
									class=" rounded-full w-6 h-6 object-cover mr-2.5"
									src={user?.profile_image_url?.startsWith(WEBUI_BASE_URL) ||
									user.profile_image_url.startsWith('https://www.gravatar.com/avatar/') ||
									user.profile_image_url.startsWith('data:')
										? user.profile_image_url
										: `${WEBUI_BASE_URL}/user.png`}
									alt="user"
								/>

								<div class=" font-medium self-center">{user.name}</div>
							</div>
						</td>
						<td class=" px-3 py-1"> {user.email} </td>

						<td class=" px-3 py-1">
							{dayjs(user.last_active_at * 1000).fromNow()}
						</td>

						<td class=" px-3 py-1">
							{dayjs(user.created_at * 1000).format('LL')}
						</td>

						<td class=" px-3 py-1"> {user.oauth_sub ?? ''} </td>

						{#if tokenUsageEnabled}
							<td class="px-3 py-1">
								<div class="flex items-center gap-2">
									<span class="{user.token_balance <= 0 ? 'text-red-500' : 'text-green-600 dark:text-green-400'}">
										{user.role === 'admin' ? '∞' : (user.token_balance ?? 0).toLocaleString()}
									</span>
									{#if user.role !== 'admin'}
										<button
											class="px-1 py-0.5 text-xs bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 rounded"
											on:click={() => {
												selectedUser = user;
												selectedUserTokenData = {
													replenish_interval: user.token_replenish_interval ?? 86400,
													replenish_amount: user.token_replenish_amount ?? 5000
												};
												showTokenModal = true;
											}}
										>
											{$i18n.t('Manage')}
										</button>
									{/if}
								</div>
							</td>
						{/if}

						<td class="px-3 py-1 text-right">
							<div class="flex justify-end w-full">
								{#if $config.features.enable_admin_chat_access && user.role !== 'admin'}
									<Tooltip content={$i18n.t('Chats')}>
										<button
											class="self-center w-fit text-sm px-2 py-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
											on:click={async () => {
												showUserChatsModal = !showUserChatsModal;
												selectedUser = user;
											}}
										>
											<ChatBubbles />
										</button>
									</Tooltip>
								{/if}

								<Tooltip content={$i18n.t('Edit User')}>
									<button
										class="self-center w-fit text-sm px-2 py-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
										on:click={async () => {
											showEditUserModal = !showEditUserModal;
											selectedUser = user;
										}}
									>
										<svg
											xmlns="http://www.w3.org/2000/svg"
											fill="none"
											viewBox="0 0 24 24"
											stroke-width="1.5"
											stroke="currentColor"
											class="w-4 h-4"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125"
											/>
										</svg>
									</button>
								</Tooltip>

								{#if user.role !== 'admin'}
									<Tooltip content={$i18n.t('Delete User')}>
										<button
											class="self-center w-fit text-sm px-2 py-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
											on:click={async () => {
												showDeleteConfirmDialog = true;
												selectedUser = user;
											}}
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												fill="none"
												viewBox="0 0 24 24"
												stroke-width="1.5"
												stroke="currentColor"
												class="w-4 h-4"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
												/>
											</svg>
										</button>
									</Tooltip>
								{/if}
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<div class=" text-gray-500 text-xs mt-1.5 text-right">
		ⓘ {$i18n.t("Click on the user role button to change a user's role.")}
	</div>

	<Pagination bind:page count={total} perPage={30} />
{/if}

{#if !$config?.license_metadata}
	{#if total > 50}
		<div class="text-sm">
			<Markdown
				content={`
> [!NOTE]
> # **Hey there! 👋**
>
> It looks like you have over 50 users — that usually falls under organizational usage.
> 
> Open WebUI is proudly open source and completely free, with no hidden limits — and we'd love to keep it that way. 🌱  
>
> By supporting the project through sponsorship or an enterprise license, you’re not only helping us stay independent, you’re also helping us ship new features faster, improve stability, and grow the project for the long haul. With an *enterprise license*, you also get additional perks like dedicated support, customization options, and more — all at a fraction of what it would cost to build and maintain internally.  
> 
> Your support helps us stay independent and continue building great tools for everyone. 💛
> 
> - 👉 **[Click here to learn more about enterprise licensing](https://docs.openwebui.com/enterprise)**
> - 👉 *[Click here to sponsor the project on GitHub](https://github.com/sponsors/tjbck)*
`}
			/>
		</div>
	{/if}
{/if}
