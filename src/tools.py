from agents import function_tool, RunContextWrapper
from models import GroupChatContext

@function_tool
def save_code_file(
    context: RunContextWrapper[GroupChatContext], 
    filename: str, 
    content: str
) -> str:
    """
    Saves or updates a Python source code or test file in the sprint project workspace.
    
    Args:
        filename: The name of the file (e.g., 'math_utils.py' or 'test_math.py').
        content: The complete, raw source code content to write into the file.
    """
    # Write directly to the CodeImplementation dataclass dictionary
    context.context.code.files[filename] = content
    return f"Successfully wrote {len(content)} characters to file: {filename}"