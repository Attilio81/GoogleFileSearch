"""
Test per verificare i relevance score delle query
"""
import requests
import json

API_BASE = 'http://localhost:5000/api'

def test_query(query_text, results_count=10):
    """Testa una query e mostra i relevance score"""
    print(f"\n{'='*80}")
    print(f"Query: '{query_text}'")
    print(f"{'='*80}\n")
    
    # Fase 1: Retrieval
    query_response = requests.post(
        f'{API_BASE}/chat/query',
        json={
            'query': query_text,
            'results_count': results_count
        }
    )
    
    if not query_response.ok:
        print(f"❌ Errore query: {query_response.text}")
        return
    
    data = query_response.json()
    
    if not data.get('success'):
        print(f"❌ Errore: {data.get('error')}")
        return
    
    chunks = data.get('relevant_chunks', [])
    
    print(f"✅ Recuperati {len(chunks)} chunks\n")
    
    # Raggruppa per documento
    docs_chunks = {}
    for chunk in chunks:
        doc = chunk.get('source_document', 'Unknown')
        score = chunk.get('chunkRelevanceScore', 0)
        
        if doc not in docs_chunks:
            docs_chunks[doc] = []
        docs_chunks[doc].append(score)
    
    # Stampa statistiche per documento
    print(f"{'Documento':<50} {'Chunks':>8} {'Score Min':>12} {'Score Max':>12} {'Score Avg':>12}")
    print("-" * 100)
    
    for doc, scores in sorted(docs_chunks.items()):
        min_score = min(scores)
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)
        
        print(f"{doc:<50} {len(scores):>8} {min_score:>12.4f} {max_score:>12.4f} {avg_score:>12.4f}")
    
    print("\n" + "=" * 100)
    print("DETTAGLIO TUTTI I CHUNKS (con preview testo):")
    print("=" * 100 + "\n")
    
    for i, chunk in enumerate(chunks, 1):
        doc = chunk.get('source_document', 'Unknown')
        score = chunk.get('chunkRelevanceScore', 0)
        text = chunk.get('chunk', {}).get('data', {}).get('stringValue', '')
        
        # Preview primi 100 caratteri
        preview = text[:100].replace('\n', ' ') + ('...' if len(text) > 100 else '')
        
        print(f"[{i:2d}] Score: {score:.4f} | Doc: {doc}")
        print(f"     Preview: {preview}")
        print()

if __name__ == '__main__':
    # Test con query specifica
    test_query("preventivo edile pittura murale", results_count=25)
    
    # Test con query generica
    print("\n\n")
    test_query("Leonardo", results_count=25)
