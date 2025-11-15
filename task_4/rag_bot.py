import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
import config
from prompts import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES


class RAGBot:
    def __init__(self, openai_api_key: str):
        print("Инициализация RAG-бота...")
        
        self.chroma_client = chromadb.PersistentClient(path=str(config.CHROMA_DB_PATH))
        
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=config.EMBEDDING_MODEL
        )
        
        self.collection = self.chroma_client.get_collection(
            name=config.COLLECTION_NAME,
            embedding_function=self.embedding_func
        )
        
        self.openai_client = OpenAI(api_key=openai_api_key)
        
        print(f"✓ ChromaDB загружена ({self.collection.count()} чанков)")
        print(f"✓ Модель эмбеддингов: {config.EMBEDDING_MODEL}")
        print(f"✓ OpenAI модель: {config.OPENAI_MODEL}")
    
    def search(self, query: str, top_k: int = None):
        if top_k is None:
            top_k = config.TOP_K_RESULTS
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        contexts = []
        for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            similarity = 1 / (1 + dist)
            contexts.append({
                'text': doc,
                'source': meta.get('source', 'unknown'),
                'chunk_id': meta.get('chunk_id', 0),
                'distance': dist,
                'similarity': similarity
            })
        
        return contexts
    
    def build_prompt(self, query: str, contexts: list):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        for example in FEW_SHOT_EXAMPLES:
            messages.append({
                "role": "user",
                "content": f"Вопрос: {example['query']}\n\nКонтекст из документа {example['source']}:\n{example['context']}"
            })
            messages.append({
                "role": "assistant",
                "content": example['answer']
            })
        
        context_text = ""
        if contexts:
            context_text = "\n\n".join([
                f"Документ {ctx['source']} (чанк {ctx['chunk_id']}, релевантность: {ctx['similarity']:.2f}):\n{ctx['text']}"
                for ctx in contexts
            ])
        else:
            context_text = "Контекст отсутствует."
        
        user_message = f"Вопрос: {query}\n\nКонтекст из базы знаний:\n{context_text}"
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def generate_answer(self, query: str, debug: bool = False):
        contexts = self.search(query)
        
        if debug:
            print(f"\n🔍 Найдено чанков: {len(contexts)}")
            for i, ctx in enumerate(contexts, 1):
                print(f"  {i}. {ctx['source']} (similarity: {ctx['similarity']:.3f})")
        
        relevant_contexts = [ctx for ctx in contexts if ctx['similarity'] > config.SIMILARITY_THRESHOLD]
        
        if not relevant_contexts:
            return "Размышление: Я просмотрел базу знаний, но не нашел достаточно релевантной информации по этому вопросу.\nОтвет: Я не знаю, эта информация отсутствует в базе знаний."
        
        messages = self.build_prompt(query, relevant_contexts)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                temperature=config.OPENAI_TEMPERATURE,
                max_tokens=config.OPENAI_MAX_TOKENS
            )
            
            answer = response.choices[0].message.content
            
            if debug:
                print(f"\n📊 Использовано токенов: {response.usage.total_tokens}")
            
            return answer
            
        except Exception as e:
            return f"Ошибка при обращении к OpenAI API: {str(e)}"

