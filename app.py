#to-do: integrate with discord client

# Setup
import os
import chromadb
import sqlite3
from ollama import Client
from chromadb.utils import embedding_functions
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
path = 'C:/Python/project_nekomimi/backend/discord-bot/db/'
OLLAMA_HOST = os.getenv('OLLAMA_HOST')
MODEL = "shoyu_v1"

# Clients
client = chromadb.PersistentClient(path=path)
ollama = Client(host=OLLAMA_HOST)


def _get_or_create_collection():
    collection = client.get_or_create_collection(
        name="history",
        configuration={
            "hnsw": {
                "space": "cosine",
                "ef_search": 100,
                "ef_construction": 100,
                "max_neighbors": 16
            },
            "embedding_function": ef
        }
    )
    return collection

def query_sql(filename,path):
    try:
        docs = []
        with sqlite3.connect(f"{path}") as conn:
            cur = conn.cursor()
            required_columns = {
                "id",
                "conversationId",
                "role",
                "status",
                "createdAt",
                "author_id",
                "author_displayName",
                "author_avatarUrl",
                "author_isOnline",
                "author_role",
                "parts_type",
                "parts_text",
            }
            cur.execute(f"""create table if not exists {filename}(
                id text primary key,
                conversationId text,
                role text,
                status text,
                createdAt text,
                author_id text,
                author_displayName text,
                author_avatarUrl text,
                author_isOnline boolean,
                author_role text,
                parts_type text,
                parts_text text
            )""")
            cur.execute(f"select parts_text from {filename}")
            docs = cur.fetchall()
            conn.commit()
        return docs
    except Exception as e:
        print(f"server.py _createtables_(): {e}")

# Each memory keeps its id, document, and metadata together so a single turn is
# easy to add/edit/remove without keeping three separate lists index-aligned.
MEMORIES = [
    {
        "id": "1",
        "document": "User greets Shoyu. Shoyu responds casually and mentions a streamer tea meme.",
        "category": "small_talk",
        "topic": "casual greeting",
        "tags": "greeting,roleplay,secretary_persona,casual_chat",
        "intent": "social",
        "accuracy": "safe",
    },
    {
        "id": "2",
        "document": "User says their eyes feel sore from reading, mentions possible dyslexia, playing Honkai Star Rail in Japanese, and learning Japanese. Shoyu gives eye strain advice but incorrectly interprets HSR as a band.",
        "category": "health",
        "topic": "health and gaming",
        "tags": "eye_strain,dyslexia_concern,Honkai_Star_Rail,Japanese_learning,assistant_misunderstanding",
        "intent": "support_and_clarification",
        "accuracy": "mixed",
    },
    {
        "id": "3",
        "document": "User corrects Shoyu that HSR is a game and asks about cat GIFs. Shoyu describes virtual cat GIFs like Nyan Cat, Pusheen, and Lil Bub.",
        "category": "entertainment",
        "topic": "cat gifs and humor",
        "tags": "cat_gifs,Nyan_Cat,Pusheen,Lil_Bub,humor,roleplay",
        "intent": "entertainment",
        "accuracy": "safe",
    },
    {
        "id": "4",
        "document": "User explains HSR means Honkai Star Rail and asks what languages Shoyu can speak. Shoyu says she mainly uses English and can help with translation, Reddit summaries, and programming explanations.",
        "category": "language_learning",
        "topic": "language capabilities",
        "tags": "Honkai_Star_Rail,Japanese,translation,language_learning,assistant_capabilities",
        "intent": "capability_discussion",
        "accuracy": "safe",
    },
    {
        "id": "5",
        "document": "User asks Shoyu to translate 君はバカです. Shoyu explains it literally means 'You are an idiot' and can be softened as teasing.",
        "category": "language_learning",
        "topic": "Japanese translation",
        "tags": "Japanese,translation,君はバカです,insult,tone",
        "intent": "translation",
        "accuracy": "mostly_safe",
    },
    {
        "id": "6",
        "document": "User asks Shoyu to write a Japanese sentence using バカ. Shoyu attempts a sentence, but the Japanese and romanization are inaccurate.",
        "category": "language_learning",
        "topic": "Japanese sentence generation",
        "tags": "Japanese,バカ,sentence_generation,language_learning",
        "intent": "language_practice",
        "accuracy": "assistant_error",
    },
    {
        "id": "7",
        "document": "User jokes about being a larping weeb and asks Shoyu to translate a Japanese Re:Zero description. Shoyu translates it but incorrectly claims it is from HSR and gets details wrong.",
        "category": "anime",
        "topic": "anime translation",
        "tags": "ReZero,Japanese_translation,isekai,Subaru_Natsuki,anime,assistant_error",
        "intent": "translation_and_identification",
        "accuracy": "assistant_error",
    },
    {
        "id": "8",
        "document": "User asks which anime the Japanese description is from. Shoyu incorrectly guesses Sword Art Online.",
        "category": "anime",
        "topic": "anime identification",
        "tags": "ReZero,Sword_Art_Online,anime_guessing,assistant_error",
        "intent": "trivia",
        "accuracy": "assistant_error",
    },
    {
        "id": "9",
        "document": "User asks Shoyu to list anime she knows. Shoyu lists popular anime across shonen, seinen, josei, shojo, and other categories.",
        "category": "anime",
        "topic": "anime list",
        "tags": "anime,shonen,seinen,shojo,josei,popular_media",
        "intent": "recommendation_or_listing",
        "accuracy": "mixed",
    },
    {
        "id": "10",
        "document": "User reveals the anime was Re:Zero, then gives another MAL-style anime description involving levels, roles, villagers, and monster hunting. Shoyu incorrectly guesses Overlord.",
        "category": "anime",
        "topic": "anime trivia",
        "tags": "ReZero,MAL,isekai,levels,roles,villagers,anime_guessing,assistant_error",
        "intent": "trivia",
        "accuracy": "assistant_error",
    },
    {
        "id": "11",
        "document": "User asks for the description of Youjo Senki. Shoyu incorrectly describes KonoSuba instead.",
        "category": "anime",
        "topic": "anime description",
        "tags": "Youjo_Senki,KonoSuba,anime_summary,assistant_error",
        "intent": "anime_explanation",
        "accuracy": "assistant_error",
    },
    {
        "id": "12",
        "document": "User gives a Re:Zero character description and asks Shoyu to guess the main character. Shoyu correctly answers Subaru Natsuki.",
        "category": "anime",
        "topic": "ReZero character trivia",
        "tags": "ReZero,Subaru_Natsuki,Emilia,Return_by_Death,Lugunica,anime_trivia",
        "intent": "trivia",
        "accuracy": "safe",
    },
    {
        "id": "13",
        "document": "User asks for popular video games. Shoyu lists games by genre, including Zelda, Dark Souls, Final Fantasy, Persona, Call of Duty, League of Legends, Minecraft, Stardew Valley, and others.",
        "category": "gaming",
        "topic": "video game list",
        "tags": "video_games,RPG,FPS,strategy,simulation,popular_games",
        "intent": "recommendation_or_listing",
        "accuracy": "safe",
    },
    {
        "id": "14",
        "document": "User asks Shoyu to guess an obscure fantasy spell-casting roguelike with relics and spell upgrades. Shoyu guesses Slay the Spire.",
        "category": "gaming",
        "topic": "roguelike game trivia",
        "tags": "roguelike,spell_casting,relics,spell_upgrades,bosses,game_guessing",
        "intent": "trivia",
        "accuracy": "uncertain",
    },
    {
        "id": "15",
        "document": "User asks if Malenia is the final boss of Dark Souls. Shoyu correctly says no, but incorrectly says Malenia is from Sekiro instead of Elden Ring.",
        "category": "gaming",
        "topic": "Dark Souls and Elden Ring trivia",
        "tags": "Dark_Souls,Malenia,Elden_Ring,Sekiro,boss_trivia,assistant_error",
        "intent": "game_trivia",
        "accuracy": "assistant_error",
    },
    {
        "id": "16",
        "document": "User corrects Shoyu that Malenia, Goddess of Rot, is from Elden Ring. Shoyu acknowledges the correction and guesses the earlier roguelike might be Hades.",
        "category": "gaming",
        "topic": "Elden Ring correction",
        "tags": "Malenia,Goddess_of_Rot,Elden_Ring,Hades,game_correction,roguelike_guessing",
        "intent": "correction_and_trivia",
        "accuracy": "mixed",
    },
    {
        "id": "17",
        "document": "User asks how to save Solaire of Astora in Dark Souls. Shoyu gives an inaccurate answer involving Manus, Father of the Abyss.",
        "category": "gaming",
        "topic": "Dark Souls guide",
        "tags": "Dark_Souls,Solaire_of_Astora,NPC_questline,game_guide,assistant_error",
        "intent": "game_help",
        "accuracy": "assistant_error",
    },
    {
        "id": "18",
        "document": "User asks what Retrieval-Augmented Generation is and requests at least one pro and con. Shoyu incorrectly describes RAG as reinforcement learning / pretraining-finetuning instead of retrieval plus generation.",
        "category": "technology",
        "topic": "RAG explanation",
        "tags": "RAG,Retrieval_Augmented_Generation,vector_database,LLM,tech,assistant_error",
        "intent": "technical_explanation",
        "accuracy": "assistant_error",
    },
    {
        "id": "19",
        "document": "User returns in the evening and says they were reading Discord API docs. Shoyu responds supportively and asks about interesting Discord API features.",
        "category": "programming",
        "topic": "Discord API study",
        "tags": "Discord_API,programming,documentation,project_update,Shoyu_bot",
        "intent": "daily_update",
        "accuracy": "safe",
    },
    {
        "id": "20",
        "document": "User says they are adding Shoyu to Discord first and may later add better long-term memory. Shoyu responds enthusiastically about Discord integration and long-term memory.",
        "category": "programming",
        "topic": "Discord integration and memory",
        "tags": "Discord_bot,long_term_memory,AI_secretary,Shoyu_integration,project_planning",
        "intent": "project_planning",
        "accuracy": "safe",
    },
    {
        "id": "21",
        "document": "User says Shoyu can chill until needed and that they are going to bed. Shoyu gives a casual goodnight.",
        "category": "small_talk",
        "topic": "goodnight roleplay",
        "tags": "goodnight,casual_chat,roleplay,secretary_persona",
        "intent": "social",
        "accuracy": "safe",
    },
    {
        "id": "22",
        "document": "User says they are reviewing Attention Is All You Need and writing an ML blog post for absolute beginners. Shoyu suggests beginner-friendly ML topics such as supervised learning, linear regression, KNN, overfitting, and preprocessing.",
        "category": "machine_learning",
        "topic": "ML blog planning",
        "tags": "Attention_Is_All_You_Need,Vaswani_2017,machine_learning,beginner_blog,Transformers",
        "intent": "learning_advice",
        "accuracy": "mostly_safe",
    },
    {
        "id": "23",
        "document": "User asks how neural networks function. Shoyu explains neurons, layers, activation functions, forward pass, backward pass, gradients, and weight updates.",
        "category": "machine_learning",
        "topic": "neural networks explanation",
        "tags": "neural_networks,activation_functions,forward_pass,backpropagation,gradients,weights",
        "intent": "technical_explanation",
        "accuracy": "mostly_safe",
    },
    {
        "id": "24",
        "document": "User checks in during the afternoon, mentions RNNs, Transformers, Python OOP textbook study, projects, and lunch. Shoyu gives a supportive productivity response.",
        "category": "programming",
        "topic": "programming study check-in",
        "tags": "RNNs,Transformers,Python_OOP,study_plan,productivity,lunch",
        "intent": "daily_update",
        "accuracy": "safe",
    },
    {
        "id": "25",
        "document": "User says they failed at implementing a mini vector database, is running out of caffeine, and finished notes on neural networks and Transformers. Shoyu encourages them and frames debugging as part of learning.",
        "category": "mental_health",
        "topic": "vector database learning reflection",
        "tags": "mini_vector_database,debugging,caffeine,Neural_Networks,Transformers,motivation",
        "intent": "emotional_support_and_learning",
        "accuracy": "safe",
    },
    {
        "id": "26",
        "document": "User says they want to see Shoyu on Discord and is excited for new capabilities. Shoyu responds with enthusiasm and a goodnight.",
        "category": "programming",
        "topic": "Discord project excitement",
        "tags": "Discord_integration,Shoyu_bot,new_capabilities,goodnight,project_motivation",
        "intent": "project_update",
        "accuracy": "safe",
    },
    {
        "id": "27",
        "document": "User says good morning. Shoyu responds with a cheerful morning greeting.",
        "category": "small_talk",
        "topic": "morning greeting",
        "tags": "morning,greeting,roleplay,secretary_persona",
        "intent": "social",
        "accuracy": "safe",
    },
]


def add_data(collection):
    collection.add(
        ids=[memory["id"] for memory in MEMORIES],
        documents=[memory["document"] for memory in MEMORIES],
        metadatas=[
            {key: value for key, value in memory.items() if key not in ("id", "document")}
            for memory in MEMORIES
        ],
    )

def query_db(collection, query):
    docs = []
    results = collection.query(
        query_texts=[query],
        n_results=3,
    )
    for idx, document in enumerate(results["documents"][0]):
        doc_id = results["ids"][0][idx]
        distance = results["distances"][0][idx]
        docs.append(document)
        print(
            f"For the query: {query}, \n Found similiar document: {document} (ID: {doc_id}, Distance: {distance})"
        )
    return docs

def save_db(collection, query):
    collection.add(
        ids=[str(collection.count()+1)],
        documents=[query],
    )

def chat(model,query):
    reply = ""
    response = ollama.chat(
        model=model,
        messages=[{'role': "user", 'content': query}],
        stream=True
    )
    for chunk in response:
        content = chunk['message']['content']
        reply += content
        print(content, end='', flush=True)
    return reply

def main():
    collection = _get_or_create_collection()
    # add_data()
    inp = input("\nQuery: ")
    while (inp.strip().lower() != "exit"):
        docs = query_db(collection,inp)
        save_db(collection,inp)
        inp += f"\nContext: {docs}\n"
        print(f"Query: {inp}")
        reply = chat(MODEL,inp)
        save_db(collection,reply)
        collection = _get_or_create_collection()
        inp = input("\nQuery: ")

if __name__ == '__main__':
    main()
    print("Program finished")


    # docs = query_sql("history","history.db")
