<script lang="ts">
  import { chatStore, connectionStore, sessionStore } from "$lib/stores";
  import { AlertCircle, X, WifiOff, LoaderCircle } from "@lucide/svelte";
  import { onMount } from "svelte";
  import MessageList from "./MessageList.svelte";
  import ChatInput from "./ChatInput.svelte";
  import EmptyState from "./EmptyState.svelte";

  const DRAG_MIME = "application/x-pocketpaw-files";

  let { initialValue = "" }: { initialValue?: string } = $props();

  let chatInput: ChatInput | undefined = $state();
  let panelEl: HTMLDivElement | undefined = $state();
  let isDragOver = $state(false);
  let isEmpty = $derived(chatStore.isEmpty && !chatStore.isStreaming);
  let error = $derived(chatStore.error);
  let isDisconnected = $derived(!connectionStore.isConnected && connectionStore.status !== "connecting");
  let isConnecting = $derived(connectionStore.status === "connecting");
  let isOffline = $derived(connectionStore.isOffline);
  let isLoadingHistory = $derived(sessionStore.isLoadingHistory);

  // ✅ NEW: stable state to stop flicker
  let showDisconnected = $state(false);

  $effect(() => {
    if (!connectionStore.isConnected && connectionStore.status !== "connecting") {
      showDisconnected = true;
    }
  });

  function handleSuggestion(text: string) {
    chatStore.sendMessage(text);
  }

  function dismissError() {
    chatStore.error = null;
  }

  function retryConnection() {
    window.location.reload();
  }

  function retryLastMessage() {
    chatStore.error = null;
    chatStore.regenerateLastResponse();
  }

  onMount(() => {
    function onDragOver(e: DragEvent) {
      if (!panelEl?.contains(e.target as Node)) {
        if (isDragOver) isDragOver = false;
        return;
      }
      e.preventDefault();
      if (e.dataTransfer) e.dataTransfer.dropEffect = "copy";
      isDragOver = true;
    }

    function onDragLeave(e: DragEvent) {
      if (!panelEl) return;
      const rect = panelEl.getBoundingClientRect();
      if (
        e.clientX <= rect.left || e.clientX >= rect.right ||
        e.clientY <= rect.top || e.clientY >= rect.bottom
      ) {
        isDragOver = false;
      }
    }

    function onDrop(e: DragEvent) {
      if (!panelEl?.contains(e.target as Node)) return;
      e.preventDefault();
      isDragOver = false;
      if (!e.dataTransfer || !chatInput) return;

      const raw = e.dataTransfer.getData(DRAG_MIME);
      if (raw) {
        try {
          const { paths } = JSON.parse(raw) as { paths: string[] };
          chatInput.addExplorerFiles(paths);
          return;
        } catch {}
      }

      if (e.dataTransfer.files.length > 0) {
        chatInput.addFiles(Array.from(e.dataTransfer.files));
      }
    }

    function onDragEnd() {
      isDragOver = false;
    }

    function onAddToChat(e: Event) {
      const detail = (e as CustomEvent).detail as { paths: string[] };
      if (detail?.paths && chatInput) {
        chatInput.addExplorerFiles(detail.paths);
      }
    }

    document.addEventListener("dragover", onDragOver);
    document.addEventListener("dragleave", onDragLeave);
    document.addEventListener("drop", onDrop);
    document.addEventListener("dragend", onDragEnd);
    window.addEventListener("explorer:add-to-chat", onAddToChat);

    return () => {
      document.removeEventListener("dragover", onDragOver);
      document.removeEventListener("dragleave", onDragLeave);
      document.removeEventListener("drop", onDrop);
      document.removeEventListener("dragend", onDragEnd);
      window.removeEventListener("explorer:add-to-chat", onAddToChat);
    };
  });
</script>

<div bind:this={panelEl} class="relative flex h-full flex-col">
  {#if isDragOver}
    <div class="pointer-events-none absolute inset-0 z-50 flex items-center justify-center rounded-lg border-2 border-dashed border-primary/50 bg-background/80 backdrop-blur-sm">
      <p class="text-sm font-medium text-primary">Drop files here</p>
    </div>
  {/if}

  {#if isLoadingHistory}
    <div class="flex flex-1 items-center justify-center">
      <LoaderCircle class="h-5 w-5 animate-spin text-muted-foreground" />
    </div>
  {:else if isEmpty}
    <div class="flex flex-1 items-center justify-center">
      <EmptyState onSuggestionClick={handleSuggestion} />
    </div>
  {:else}
    <MessageList />
  {/if}

  {#if isOffline}
    <div class="mx-4 mb-2 flex items-center gap-2 rounded-md border border-yellow-500/20 bg-yellow-500/10 px-3 py-2 text-sm text-yellow-400">
      <WifiOff class="h-4 w-4 shrink-0" />
      <span class="flex-1">You're offline. Waiting for network connection...</span>
    </div>

  {:else if showDisconnected || isConnecting}
    <div class="mx-4 mb-2 flex items-center gap-2 rounded-md border border-yellow-500/20 bg-yellow-500/10 px-3 py-2 text-sm text-yellow-400">
      <WifiOff class="h-4 w-4 shrink-0" />

      <div class="flex flex-1 items-center justify-between gap-2">
        <span>
          {#if isConnecting && !showDisconnected}
            Connecting to backend...
          {:else}
            ⚠️ Backend not connected. Please start the server.
          {/if}
        </span>

        {#if showDisconnected}
          <button
            onclick={retryConnection}
            class="rounded-sm bg-yellow-500/20 px-2 py-1 text-xs font-medium hover:bg-yellow-500/30"
          >
            Retry
          </button>
        {/if}
      </div>
    </div>
  {/if}

  {#if error}
    <div class="mx-4 mb-2 flex items-center gap-2 rounded-md border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm text-red-400">
      <AlertCircle class="h-4 w-4 shrink-0" />
      <span class="flex-1">{error}</span>
      {#if chatStore.messages.length > 0}
        <button onclick={retryLastMessage} class="shrink-0 rounded-sm px-2 py-0.5 text-xs font-medium hover:bg-red-500/20">
          Retry
        </button>
      {/if}
      <button onclick={dismissError} class="shrink-0 rounded-sm p-0.5 hover:bg-red-500/20">
        <X class="h-3.5 w-3.5" />
      </button>
    </div>
  {/if}

  <ChatInput bind:this={chatInput} {initialValue} />
</div>