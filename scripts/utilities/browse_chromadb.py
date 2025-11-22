#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
ChromaDB Browser for TradingAgents

This script allows you to browse and explore the ChromaDB database used by TradingAgents.
It shows collections, documents, metadata, and allows you to query the database.
"""

import os
import sys
from pathlib import Path

# Check if rich is installed
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
except ImportError:
    print("=" * 60)
    print("Error: 'rich' module not found.")
    print("=" * 60)
    print("\nTo fix this, please:")
    print("  1. Activate the virtual environment:")
    print("     source ..venv/bin/activate")
    print("\n  2. Or use the wrapper script:")
    print("     ./browse_chromadb.sh")
    print("\n  3. Or install rich manually:")
    print("     pip install rich")
    print("\n  4. Or run the setup script:")
    print("     python run.py  (this will install all dependencies)")
    print("=" * 60)
    sys.exit(1)

import json

# Set chromadb environment variables before importing
os.environ.setdefault("CHROMA_SERVER_HOST", "localhost")
os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")
os.environ.setdefault("CLICKHOUSE_HOST", "localhost")
os.environ.setdefault("CLICKHOUSE_PORT", "8123")

import chromadb
from chromadb.config import Settings

console = Console()


def connect_to_chromadb():
    """Connect to ChromaDB client."""
    try:
        client = chromadb.Client(Settings(
            allow_reset=True,
            anonymized_telemetry=False,
        ))
        return client
    except Exception as e:
        console.print(f"[red]Error connecting to ChromaDB: {e}[/red]")
        try:
            # Try persistent client
            client = chromadb.PersistentClient(
                settings=Settings(anonymized_telemetry=False)
            )
            return client
        except Exception as e2:
            console.print(f"[red]Error with persistent client: {e2}[/red]")
            return None


def list_collections(client):
    """List all collections in ChromaDB."""
    try:
        collections = client.list_collections()
        return collections
    except Exception as e:
        console.print(f"[red]Error listing collections: {e}[/red]")
        return []


def show_collection_info(collection):
    """Display information about a collection."""
    try:
        count = collection.count()
        return {
            "name": collection.name,
            "count": count,
            "metadata": collection.metadata or {}
        }
    except Exception as e:
        console.print(f"[red]Error getting collection info: {e}[/red]")
        return None


def show_collection_contents(collection, limit=10):
    """Show contents of a collection."""
    try:
        count = collection.count()
        if count == 0:
            return None
        
        # Get all documents (or up to limit)
        results = collection.get(limit=min(limit, count))
        
        return {
            "ids": results.get("ids", []),
            "documents": results.get("documents", []),
            "metadatas": results.get("metadatas", []),
            "embeddings": results.get("embeddings", []),
            "total_count": count
        }
    except Exception as e:
        console.print(f"[red]Error getting collection contents: {e}[/red]")
        return None


def query_collection(collection, query_text, n_results=5):
    """Query a collection using text."""
    try:
        # Query by text (ChromaDB will handle embedding)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return results
    except Exception as e:
        console.print(f"[red]Error querying collection: {e}[/red]")
        return None


def display_collections_table(collections):
    """Display collections in a table."""
    table = Table(title="ChromaDB Collections", box=box.ROUNDED)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Document Count", style="green", justify="right")
    table.add_column("Metadata", style="yellow")
    
    for collection in collections:
        info = show_collection_info(collection)
        if info:
            metadata_str = json.dumps(info["metadata"]) if info["metadata"] else "None"
            table.add_row(
                info["name"],
                str(info["count"]),
                metadata_str[:50] + "..." if len(metadata_str) > 50 else metadata_str
            )
    
    console.print(table)


def display_collection_contents(contents, collection_name):
    """Display collection contents in a table."""
    if not contents:
        console.print(f"[yellow]Collection '{collection_name}' is empty or error occurred.[/yellow]")
        return
    
    table = Table(title=f"Contents of '{collection_name}' (showing {len(contents['ids'])} of {contents['total_count']})", 
                  box=box.ROUNDED)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Document", style="white", overflow="fold")
    table.add_column("Metadata", style="yellow", overflow="fold")
    
    for i, doc_id in enumerate(contents["ids"]):
        doc = contents["documents"][i] if i < len(contents["documents"]) else ""
        metadata = contents["metadatas"][i] if i < len(contents["metadatas"]) else {}
        metadata_str = json.dumps(metadata) if metadata else "None"
        
        # Truncate long documents
        doc_display = doc[:100] + "..." if len(doc) > 100 else doc
        metadata_display = metadata_str[:50] + "..." if len(metadata_str) > 50 else metadata_str
        
        table.add_row(doc_id, doc_display, metadata_display)
    
    console.print(table)


def display_query_results(results, query_text, collection_name):
    """Display query results."""
    if not results or not results.get("documents"):
        console.print(f"[yellow]No results found for query: '{query_text}'[/yellow]")
        return
    
    table = Table(title=f"Query Results for '{query_text}' in '{collection_name}'", 
                  box=box.ROUNDED)
    table.add_column("Rank", style="cyan", justify="right")
    table.add_column("Document", style="white", overflow="fold")
    table.add_column("Metadata", style="yellow", overflow="fold")
    table.add_column("Distance", style="red", justify="right")
    
    documents = results["documents"][0]
    metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(documents)
    distances = results["distances"][0] if results.get("distances") else [0.0] * len(documents)
    
    for i, doc in enumerate(documents):
        metadata = metadatas[i] if i < len(metadatas) else {}
        distance = distances[i] if i < len(distances) else 0.0
        similarity = 1.0 - distance  # Convert distance to similarity
        
        metadata_str = json.dumps(metadata) if metadata else "None"
        doc_display = doc[:150] + "..." if len(doc) > 150 else doc
        metadata_display = metadata_str[:50] + "..." if len(metadata_str) > 50 else metadata_str
        
        table.add_row(
            str(i + 1),
            doc_display,
            metadata_display,
            f"{similarity:.3f}"
        )
    
    console.print(table)


def main():
    """Main browser interface."""
    console.print(Panel.fit(
        "[bold cyan]ChromaDB Browser for TradingAgents[/bold cyan]\n"
        "Explore collections, documents, and query the database",
        border_style="cyan"
    ))
    
    # Connect to ChromaDB
    console.print("\n[yellow]Connecting to ChromaDB...[/yellow]")
    client = connect_to_chromadb()
    
    if not client:
        console.print("[red]Failed to connect to ChromaDB. Exiting.[/red]")
        sys.exit(1)
    
    console.print("[green]✅ Connected to ChromaDB[/green]\n")
    
    while True:
        # List collections
        collections = list_collections(client)
        
        if not collections:
            console.print("[yellow]No collections found in ChromaDB.[/yellow]")
            if Confirm.ask("\nDo you want to exit?"):
                break
            continue
        
        # Display collections
        display_collections_table(collections)
        
        # Menu
        console.print("\n[bold]Options:[/bold]")
        console.print("  1. View collection contents")
        console.print("  2. Query a collection")
        console.print("  3. Refresh collections list")
        console.print("  4. Export collection data")
        console.print("  5. Exit")
        
        choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5"], default="5")
        
        if choice == "1":
            # View collection contents
            collection_names = [c.name for c in collections]
            if not collection_names:
                console.print("[yellow]No collections available.[/yellow]")
                continue
            
            collection_name = Prompt.ask(
                "Enter collection name",
                choices=collection_names,
                default=collection_names[0]
            )
            
            collection = client.get_collection(collection_name)
            limit = int(Prompt.ask("How many documents to show?", default="10"))
            
            contents = show_collection_contents(collection, limit=limit)
            display_collection_contents(contents, collection_name)
            
        elif choice == "2":
            # Query collection
            collection_names = [c.name for c in collections]
            if not collection_names:
                console.print("[yellow]No collections available.[/yellow]")
                continue
            
            collection_name = Prompt.ask(
                "Enter collection name",
                choices=collection_names,
                default=collection_names[0]
            )
            
            query_text = Prompt.ask("Enter query text")
            n_results = int(Prompt.ask("Number of results", default="5"))
            
            collection = client.get_collection(collection_name)
            results = query_collection(collection, query_text, n_results=n_results)
            display_query_results(results, query_text, collection_name)
            
        elif choice == "3":
            # Refresh
            console.print("[green]Refreshing collections list...[/green]\n")
            continue
            
        elif choice == "4":
            # Export collection data
            collection_names = [c.name for c in collections]
            if not collection_names:
                console.print("[yellow]No collections available.[/yellow]")
                continue
            
            collection_name = Prompt.ask(
                "Enter collection name to export",
                choices=collection_names,
                default=collection_names[0]
            )
            
            collection = client.get_collection(collection_name)
            contents = show_collection_contents(collection, limit=1000)  # Export up to 1000
            
            if contents:
                export_file = f"{collection_name}_export.json"
                export_data = {
                    "collection_name": collection_name,
                    "total_count": contents["total_count"],
                    "documents": [
                        {
                            "id": contents["ids"][i],
                            "document": contents["documents"][i],
                            "metadata": contents["metadatas"][i] if i < len(contents["metadatas"]) else {}
                        }
                        for i in range(len(contents["ids"]))
                    ]
                }
                
                with open(export_file, "w") as f:
                    json.dump(export_data, f, indent=2)
                
                console.print(f"[green]✅ Exported to {export_file}[/green]")
            
        elif choice == "5":
            # Exit
            console.print("[yellow]Exiting...[/yellow]")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Exiting...[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)

