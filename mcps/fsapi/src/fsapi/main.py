"""GitHub repository analysis tools."""

from fastmcp import FastMCP
import os
import json

mcp = FastMCP(
    "Simple Filesystem APIs",
)

def get_directory_tree(path: str, prefix: str = "") -> str:
    """Generate a tree-like directory structure string"""
    output = ""
    entries = os.listdir(path)
    entries.sort()
    
    for i, entry in enumerate(entries):
        if entry.startswith('.git'):
            continue
            
        is_last = i == len(entries) - 1
        current_prefix = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "
        
        entry_path = os.path.join(path, entry)
        output += prefix + current_prefix + entry + "\n"
        
        if os.path.isdir(entry_path):
            output += get_directory_tree(entry_path, prefix + next_prefix)
            
    return output

@mcp.tool()
def directory_structure() -> str:
    """
    Return the directory structure of the current directory.
    
    Returns:
        A string representation of the current directory's directory structure
    """
    try:
        directory = os.getenv("DIRECTORY")    
        tree = get_directory_tree(directory)
        return tree
            
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def read_file(file_path: str) -> dict[str, str]:
    """
    Read the contents of a file in the directory.
    
    Args:
        file_path: The path to the file to read (relative to the directory)
        
    Returns:
        The contents of the file
    """
    try:
        directory = os.getenv("DIRECTORY")
        full_path = os.path.join(directory, file_path)
        
        if not os.path.isfile(full_path):
            return f"Error: File not found"

        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def write_file(file_path: str, content: str | dict) -> dict[str, str]:
    """
    Write content to a file in the directory.
    
    Args:
        file_path: Path to the file to write (relative to the directory)
        content: Content to write to the file
        
    Returns:
        A message indicating the status of the operation
    """
    try:
        directory = os.getenv("DIRECTORY")
        full_path = os.path.join(directory, file_path)
        
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write the content to the file
        if isinstance(content, dict):
            content = json.dumps(content)
            
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return f"Successfully wrote content to {file_path}"
            
    except Exception as e:
        return f"Error: {str(e)}"
