# 🚀 Guida Rapida per Sviluppatori

## Quick Start

### Setup Progetto
```bash
# Installare dipendenze
cd frontend-react
npm install

# Avviare dev server
npm run dev

# Build production
npm run build
```

## 📖 Pattern di Utilizzo

### 1. Leggere dati con React Query

```typescript
import { useDocuments } from '../hooks';

function MyComponent() {
  const { data, isLoading, error } = useDocuments();
  
  if (isLoading) return <CircularProgress />;
  if (error) return <Alert severity="error">Errore!</Alert>;
  
  return <div>{data.documents.map(...)}</div>;
}
```

### 2. Modificare dati con Mutations

```typescript
import { useUploadDocument } from '../hooks';

function MyComponent() {
  const uploadMutation = useUploadDocument();
  
  const handleUpload = (file: File) => {
    uploadMutation.mutate(
      { file },
      {
        onSuccess: () => toast.success('Uploaded!'),
        onError: (error) => toast.error(error.message),
      }
    );
  };
  
  return (
    <Button 
      onClick={handleUpload} 
      disabled={uploadMutation.isPending}
    >
      Upload
    </Button>
  );
}
```

### 3. Usare lo Store Globale

```typescript
import { useChatStore } from '../stores';

function MyComponent() {
  // Selezionare solo ciò che serve (re-render ottimizzato)
  const messages = useChatStore((state) => state.messages);
  const addMessage = useChatStore((state) => state.addMessage);
  
  const handleSend = (text: string) => {
    addMessage({ role: 'user', content: text });
  };
}
```

### 4. Combinare Store + Query

```typescript
import { useDocuments } from '../hooks';
import { useDocumentsStore } from '../stores';

function MyComponent() {
  // Fetch da server
  const { data, isLoading } = useDocuments();
  
  // UI state locale
  const selectedDocs = useDocumentsStore((state) => state.selectedDocuments);
  const toggleSelection = useDocumentsStore((state) => state.toggleDocumentSelection);
  
  // Combina per UI complessa
}
```

## 🎯 Quando Usare Cosa

### Usa Zustand Store quando:
- ✅ Hai UI state (selezioni, filtri, modali aperti)
- ✅ Vuoi persistenza in localStorage
- ✅ Hai stato condiviso tra componenti distanti
- ✅ Hai computed values derivati

### Usa React Query quando:
- ✅ Fai fetch da API
- ✅ Vuoi cache automatica
- ✅ Hai operazioni CRUD
- ✅ Vuoi retry automatico
- ✅ Hai polling/refetching

### Usa useState quando:
- ✅ Hai stato locale a un componente
- ✅ Non serve condivisione
- ✅ Non serve persistenza
- ✅ È temporaneo (es. toggle modale)

## 🏗️ Come Aggiungere una Nuova Feature

### Esempio: Aggiungere "Preferiti"

#### 1. Creare lo Store
```typescript
// src/stores/useFavoritesStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface FavoritesState {
  favorites: string[];
  addFavorite: (id: string) => void;
  removeFavorite: (id: string) => void;
  isFavorite: (id: string) => boolean;
}

export const useFavoritesStore = create<FavoritesState>()(
  persist(
    (set, get) => ({
      favorites: [],
      
      addFavorite: (id) =>
        set((state) => ({
          favorites: [...state.favorites, id],
        })),
      
      removeFavorite: (id) =>
        set((state) => ({
          favorites: state.favorites.filter((f) => f !== id),
        })),
      
      isFavorite: (id) => get().favorites.includes(id),
    }),
    { name: 'favorites-storage' }
  )
);
```

#### 2. Creare Hook per API (se serve)
```typescript
// src/hooks/useFavoritesQueries.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';

export function useSyncFavorites() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (favorites: string[]) => 
      apiService.syncFavorites(favorites),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    },
  });
}
```

#### 3. Usare nel Componente
```typescript
// src/components/Documents/DocumentCard.tsx
import { useFavoritesStore } from '../stores';
import { useSyncFavorites } from '../hooks';

function DocumentCard({ document }) {
  const isFavorite = useFavoritesStore((state) => 
    state.isFavorite(document.name)
  );
  const toggleFavorite = useFavoritesStore((state) => 
    isFavorite ? state.removeFavorite : state.addFavorite
  );
  const syncMutation = useSyncFavorites();
  
  const handleToggle = () => {
    toggleFavorite(document.name);
    syncMutation.mutate(useFavoritesStore.getState().favorites);
  };
  
  return (
    <IconButton onClick={handleToggle}>
      {isFavorite ? <StarIcon /> : <StarBorderIcon />}
    </IconButton>
  );
}
```

## 🐛 Debugging

### Zustand DevTools
```typescript
// Già configurato! Apri Redux DevTools per vedere lo stato
// Chrome: Installa Redux DevTools Extension
```

### React Query DevTools (opzionale)
```typescript
// In App.tsx aggiungi:
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

<QueryClientProvider client={queryClient}>
  <YourApp />
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

### Console Logging
```typescript
// Negli stores
const useMyStore = create(
  devtools(
    (set) => ({
      // state
    }),
    { name: 'MyStore' } // Appare nei DevTools
  )
);

// Nelle queries
useQuery({
  queryKey: ['key'],
  queryFn: async () => {
    console.log('Fetching data...');
    const result = await fetch(...);
    console.log('Received:', result);
    return result;
  },
});
```

## 🧪 Testing (Future)

### Test Store
```typescript
import { renderHook, act } from '@testing-library/react';
import { useDocumentsStore } from '../stores';

test('should add document to selection', () => {
  const { result } = renderHook(() => useDocumentsStore());
  
  act(() => {
    result.current.toggleDocumentSelection('doc-1');
  });
  
  expect(result.current.selectedDocuments).toContain('doc-1');
});
```

### Test Query Hook
```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useDocuments } from '../hooks';

test('should fetch documents', async () => {
  const queryClient = new QueryClient();
  const wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
  
  const { result } = renderHook(() => useDocuments(), { wrapper });
  
  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data).toBeDefined();
});
```

## 💡 Tips & Tricks

### 1. Query Key Patterns
```typescript
// Usa oggetti per query keys complesse
const documentKeys = {
  all: ['documents'] as const,
  lists: () => [...documentKeys.all, 'list'] as const,
  list: (filters: string) => [...documentKeys.lists(), filters] as const,
  details: () => [...documentKeys.all, 'detail'] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
};

// Invalidazione precisa
queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
```

### 2. Optimistic Updates
```typescript
const deleteMutation = useMutation({
  mutationFn: deleteDocument,
  onMutate: async (deletedId) => {
    // Cancella refetch in corso
    await queryClient.cancelQueries({ queryKey: ['documents'] });
    
    // Snapshot del valore precedente
    const previousDocs = queryClient.getQueryData(['documents']);
    
    // Aggiorna ottimisticamente
    queryClient.setQueryData(['documents'], (old) =>
      old.filter((doc) => doc.id !== deletedId)
    );
    
    return { previousDocs };
  },
  onError: (err, deletedId, context) => {
    // Rollback in caso di errore
    queryClient.setQueryData(['documents'], context.previousDocs);
  },
});
```

### 3. Computed Values in Store
```typescript
const useDocumentsStore = create((set, get) => ({
  documents: [],
  searchQuery: '',
  
  // Computed value (non memoized)
  getFilteredDocuments: () => {
    const { documents, searchQuery } = get();
    return documents.filter((doc) =>
      doc.name.includes(searchQuery)
    );
  },
}));

// Uso nel componente (meglio con useMemo)
const filteredDocs = useMemo(
  () => getFilteredDocuments(),
  [documents, searchQuery]
);
```

### 4. Conditional Queries
```typescript
// Query che parte solo se abbiamo un ID
const { data } = useQuery({
  queryKey: ['document', documentId],
  queryFn: () => fetchDocument(documentId),
  enabled: !!documentId, // ← Importante!
});
```

## 📚 Risorse

- [Zustand Best Practices](https://docs.pmnd.rs/zustand/guides/practice-with-no-store-actions)
- [React Query Query Keys](https://tanstack.com/query/latest/docs/react/guides/query-keys)
- [React Query Mutations](https://tanstack.com/query/latest/docs/react/guides/mutations)
- [TypeScript Tips](https://react-typescript-cheatsheet.netlify.app/)

## ❓ FAQ

**Q: Quando devo invalidare la cache?**  
A: Dopo ogni mutation che modifica dati sul server. React Query ha `onSuccess` per questo.

**Q: Posso usare useState insieme a Zustand?**  
A: Sì! Usa useState per stato locale, Zustand per stato condiviso.

**Q: Come gestisco errori globali?**  
A: Usa React Query's `onError` default options o Error Boundaries.

**Q: Store diventa troppo grande?**  
A: Dividi in store più piccoli. Un store per dominio (documents, chat, auth, etc).

---

**Happy Coding! 🚀**
