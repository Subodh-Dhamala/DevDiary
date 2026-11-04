from sqlalchemy.ext.asyncio import AsyncSession

from app.services.entry_service import search_entries
from app.services.generation_service import generate_answer


async def ask_question(question: str, session: AsyncSession):

    #retrieve relevant entries
    entries = await search_entries(question, session)

    #avoid unnecessary api call
    if not entries:
        return {
            "answer": "I don't have enough information in your saved entries...",
            "sources": [],
        }

    #build context from retrieved entries using generator expression and join
    context = "\n\n".join(
        f"Title: {entry.title}\nContent: {entry.content}"
        for entry in entries
    )

    #prompt
    prompt = f"""
    You are DevDiary, an assistant that answers questions using the user's saved notes.

    Rules:
    - Answer using only the information in the provided context.
    - Do not use outside knowledge or make assumptions.
    - If the context does not contain enough information, say:
      "I don't have enough information in your saved entries."
    - If only part of the answer is available, explain what is known
      and what information is missing.
    - Do not invent facts.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    #generate answer
    answer = await generate_answer(prompt)

    #extract sources by list comprehension
    sources = [
        {
            "id": entry.id,
            "title": entry.title,
        }
        for entry in entries
    ]

    return {
        "answer": answer,
        "sources": sources,
    }