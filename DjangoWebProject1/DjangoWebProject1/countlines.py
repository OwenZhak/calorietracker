import os

def count_lines(directory='.', extensions=None, exclude_dirs=None, exclude_files=None):
    """
    Count lines of code in the specified directory.
    
    Args:
        directory (str): Directory to start counting from
        extensions (list): File extensions to count (e.g., ['.py', '.html'])
        exclude_dirs (list): Directories to exclude
        exclude_files (list): Specific files to exclude
    """
    if extensions is None:
        extensions = ['.py', '.html', '.js', '.css']
    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', 'migrations', 'env', 'venv', '.git']
    if exclude_files is None:
        exclude_files = ['bootstrap.css', 'bootstrap.min.css', 'jquery', 'modernizr']
    
    total_lines = 0
    file_count = 0
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            # Skip excluded files
            if any(excluded in file for excluded in exclude_files):
                continue
                
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        line_count = sum(1 for _ in f)
                    total_lines += line_count
                    file_count += 1
                    print(f"{file_path}: {line_count} lines")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    print(f"\nTotal: {total_lines} lines in {file_count} files")
    return total_lines

if __name__ == "__main__":
    count_lines()