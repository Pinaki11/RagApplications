import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from langsmith import traceable
from openai import AzureOpenAI

from build_chromadb import CHROMA_DIR, COLLECTION_NAME, query_policies
#from azure.identity import DefaultAzureCredential, get_bearer_token_provider


# Load repository-local configuration without committing secrets into Python code.
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Azure OpenAI uses the deployment name in the model parameter.
DEFAULT_DEPLOYMENT = "gpt-4.1-nano"
DEFAULT_API_VERSION = "2024-12-01-preview"
#token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")


# Retrieve the nearest policy pages from the persistent Chroma collection.
@traceable(name="retrieve_policy_chunks", run_type="retriever")
def retrieve_chunks(query, n_results=5, where=None):
    """Return retrieved page text and metadata for a user query."""
    result = query_policies(query, where=where, n_results=n_results)
    chunks = []
    for document, metadata in zip(result["documents"][0], result["metadatas"][0]):
        chunks.append({"text": document, "metadata": metadata})
    return chunks


# Format retrieval results so the LLM can cite the source policy and page.
def format_context(chunks):
    """Build a clearly separated context block for the generation prompt."""
    sections = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        source = metadata.get("source", "unknown source")
        page = metadata.get("page", "unknown page")
        company = metadata.get("company", "unknown company")
        sections.append(
            f"[Chunk {index} | Company: {company} | Source: {source} | Page: {page}]\n"
            f"{chunk['text']}"
        )
    return "\n\n".join(sections)


# Create an Azure OpenAI client from environment variables without storing secrets in code.
def create_azure_client():
    """Create an authenticated Azure OpenAI client."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not endpoint or not api_key:
        raise RuntimeError(
            "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY before requesting an LLM response."
        )
    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", DEFAULT_API_VERSION),
    )


# Ask the Azure OpenAI deployment to answer only from the retrieved policy context.
@traceable(name="azure_openai_generation", run_type="llm")
def generate_answer(query, chunks, model=None, conversation=None):
    """Generate a grounded answer using the retrieved chunks as context."""
    if not chunks:
        return "No relevant policy chunks were found."

    client = create_azure_client()
    selected_model = model or os.getenv("AZURE_OPENAI_DEPLOYMENT", DEFAULT_DEPLOYMENT)
    context = format_context(chunks)
    messages = [
        {
            "role": "system",
            "content": (
                "You answer questions about the supplied health insurance policy excerpts. "
                "Use only the provided context. If the answer is not in the context, say so. "
                "Always state the page number where each key fact was found, using wording such as 'According to page 3'. "
                "Include the company name when it helps distinguish policies. "
                "These documents are fictional and should not be presented as real insurance advice."
            ),
        }
    ]
    if conversation:
        messages.extend(conversation[-8:])
    messages.append(
        {
            "role": "user",
            "content": f"Question: {query}\n\nRetrieved policy context:\n{context}",
        }
    )
    response = client.chat.completions.create(
        model=selected_model,
        temperature=0,
        messages=messages,
    )
    return response.choices[0].message.content


# Trace a complete chat turn so retrieval and generation can be compared in LangSmith.
@traceable(name="insurance_query_turn", run_type="chain")
def answer_query(query, n_results=5, where=None, model=None, conversation=None):
    """Retrieve policy context and generate one grounded answer."""
    chunks = retrieve_chunks(query, n_results=n_results, where=where)
    answer = generate_answer(query, chunks, model=model, conversation=conversation)
    return {"answer": answer, "chunks": chunks}


# Print the retrieved context when testing retrieval without an API call.
def print_chunks(chunks):
    """Print chunk metadata and text for inspection."""
    for index, chunk in enumerate(chunks, start=1):
        print(f"--- Retrieved chunk {index} ---")
        print(chunk["metadata"])
        print(chunk["text"])
        print()


# Parse a query from the command line and run retrieval-augmented generation.
def main():
    parser = argparse.ArgumentParser(description="Query policy embeddings and generate an LLM answer.")
    parser.add_argument("query", help="Question to ask about the insurance policies")
    parser.add_argument("--n-results", type=int, default=5, help="Number of policy chunks to retrieve")
    parser.add_argument(
        "--model",
        help="Azure OpenAI deployment name; defaults to AZURE_OPENAI_DEPLOYMENT",
    )
    parser.add_argument(
        "--retrieve-only",
        action="store_true",
        help="Print retrieved chunks without calling the LLM",
    )
    args = parser.parse_args()

    if args.retrieve_only:
        chunks = retrieve_chunks(args.query, n_results=args.n_results)
        print(f"Retrieved {len(chunks)} chunks from {CHROMA_DIR} ({COLLECTION_NAME}).\n")
        print_chunks(chunks)
        return
    result = answer_query(args.query, n_results=args.n_results, model=args.model)
    print(f"Retrieved {len(result['chunks'])} chunks from {CHROMA_DIR} ({COLLECTION_NAME}).\n")
    print(result["answer"])


if __name__ == "__main__":
    main()